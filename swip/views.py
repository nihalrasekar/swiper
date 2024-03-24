from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Profile,ChatRoom, Messages
from rest_framework.views import APIView
from django.contrib.auth import authenticate,login
from rest_framework.permissions import IsAuthenticated
from .serializer import ProfileSerializer,ChatRoomDetailsSerializer,MessageSerializer,SendMessageSerializer
from django.contrib.sessions.models import Session
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView,RetrieveAPIView
class UserRegistration(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        last_name = request.data.get('last_name')
        first_name = request.data.get('first_name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        age = request.data.get('age')
        profile_picture = request.data.get('profile_picture')
        status = request.data.get('status')
        language = request.data.get('language')
        gender = request.data.get('gender')
        name = request.data.get('name')
        position = request.data.get('position')

        if not username or not password or not first_name or not last_name or not email or not phone_number or not age or not language or not status or not profile_picture or not name or not position:
            return Response({"error": "want all the field"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, password=password, first_name=first_name, last_name=last_name, email=email)
         # Log the user in and create a session
        session = SessionStore()
        session['user_id'] = user.pk
        session.create()

        Profile.objects.create(user=user, phone_number=phone_number, age=age,
                               profile_picture=profile_picture, status=status, languages_known=language,gender=gender,name=name,position=position)
        # Created the token for nre user
    
        return Response({"token": session.session_key}, status=status.HTTP_201_Created)


class TokenView(APIView):
    def post(self, request):
        # Get username and password from request data
        username = request.data.get('username')
        password = request.data.get('password')
        print(username,password)
        # Create a new user
        user = authenticate(username=username, password=password)
        print(user)
        # Generate a token for the user
        if user is not None:
            login(request,user)
            request.session.save()
            session_key = request.session.session_key

            return Response({"sessionId":session_key}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Error":"Invalid Creditionals"}, status=status.HTTP_401_UNAUTHORIZED)


class OptionsMatches(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Fetch the associated Profile instance for the authenticated user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare user data including fields from the Profile model
        other_users = Profile.objects.exclude(Q(user=user) | Q(gender=profile.gender))
        # This variable to return the list of account
        other_users_data = []
        for other_user_profile in other_users:
         # find the comman language
         common_languages = set(profile.languages_known) & set(other_user_profile.languages_known)
         if common_languages:
            serializer = ProfileSerializer(other_user_profile)
            other_users_data.append(serializer.data)
        return Response({'other_users_data': other_users_data})
    

def create_chat_room(user1, user2):
    """
    Create a chat room between two users.
    """
    return ChatRoom.objects.create(user1=user1, user2=user2)

"""class CreateChatRoom(APIView):
    def post(self, request):
        user1 = request.user
        other_user_id = request.data.get('other_user_id')
        if not other_user_id:
            return Response({'error': 'Other user ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        other_user = get_object_or_404(User, pk=other_user_id)

        existing_chat_room = ChatRoom.objects.filter(user1=user1, user2=other_user) | \
                             ChatRoom.objects.filter(user1=other_user, user2=user1)
        if existing_chat_room.exists():
            return Response({'error': 'Chat Room already exists'}, status=status.HTTP_400_BAD_REQUEST)

        chat_room = create_chat_room(user1, other_user)
        return Response({'chat_room_id': chat_room.id}, status=status.HTTP_201_CREATED)"""

class SendMessage(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user1 = request.user
        other_user_id = request.data.get('other_user_id')
        message_text = request.data.get("message_text")
        if not other_user_id or not message_text:
            return Response({'error': 'Other user ID and message text are required'}, status=status.HTTP_400_BAD_REQUEST)

        other_user = get_object_or_404(User, pk=other_user_id)

        chat_room = ChatRoom.objects.filter(user1=user1, user2=other_user) | \
                    ChatRoom.objects.filter(user1=other_user, user2=user1)
        if not chat_room.exists():
            chat_room = create_chat_room(user1, other_user)
        else:
            chat_room = chat_room.first()

        message = Messages.objects.create(chatroom=chat_room, user=user1, text=message_text)
        return Response({'message_id': message.id}, status=status.HTTP_201_CREATED)


class DailyStatusMediaUpload(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        media_file = request.FILES.get('media_file')

        # Check if user already has a daily status media
        if profile.dailystatus_media:
            # Delete the previous daily status media file
            profile.dailystatus_media.delete()

        # Set the new daily status media
        profile.dailystatus_media = media_file
        profile.save()

        return Response({'message': 'Daily status media uploaded successfully'}, status=status.HTTP_201_CREATED)

class UserChatRooms(APIView):
    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(user1=user) | ChatRoom.objects.filter(user2=user)
        serializer = ChatRoomDetailsSerializer(chat_rooms, many=True, context={'request': request})
        return Response(serializer.data)
    
    class ChatRoomMessages(APIView):
      def get(self, request, chat_id):
        messages = Messages.objects.filter(chatroom_id=chat_id).order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
      

# views.py


class SendMessageToChatRoom(APIView):
    def post(self, request):
        serializer = SendMessageSerializer(data=request.data)
        if serializer.is_valid():
            chatroom_id = serializer.validated_data['chatroom_id']
            user_id = serializer.validated_data['user_id']
            message_text = serializer.validated_data['message']
            
            try:
                chat_room = ChatRoom.objects.get(id=chatroom_id)
            except ChatRoom.DoesNotExist:
                return Response({'error': 'Chat room does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if the user is a member of the chat room
            if user_id not in [chat_room.user1.id, chat_room.user2.id]:
                return Response({'error': 'User is not a member of the chat room'}, status=status.HTTP_403_FORBIDDEN)
            
            # Create and save the message
            message = Messages.objects.create(chatroom=chat_room, user_id=user_id, text=message_text)
            
            return Response({'message_id': message.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class LikeSuperLikeView(APIView):
    def post(self, request, profile_id):
        action = request.data.get('action')
        user_id = request.data.get('user_id')  # ID of the user sending the super like

        profile = get_object_or_404(Profile, pk=profile_id)
        user = request.user  # Assuming the logged-in user is sending the action

        if action == 'like':
            profile.add_like()
            return Response({'message': 'Like added successfully'}, status=status.HTTP_200_OK)
        elif action == 'super_like':
            if user_id is None:
                return Response({'error': 'User ID is required for super like'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch the user sending the super like
            sender = get_object_or_404(User, pk=user_id)

            # Attempt to add the super like
            success = profile.add_super_like(sender)
            if success:
                return Response({'message': 'Super like added successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Super like not added. Limit exceeded or already sent.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            

class UserProfileView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.get(user=self.request.user)
    
class ProfileView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile