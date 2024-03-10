from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Profile,ChatRoom, Messages
from rest_framework.views import APIView
from django.contrib.auth import authenticate,login
from rest_framework.permissions import IsAuthenticated
from .serializer import ProfileSerializer
from django.contrib.sessions.models import Session
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest


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

        if not username or not password or not first_name or not last_name or not email or not phone_number or not age or not language or not status or not profile_picture:
            return Response({"error": "want all the field"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, password=password, first_name=first_name, last_name=last_name, email=email)
         # Log the user in and create a session
        session = SessionStore()
        session['user_id'] = user.pk
        session.create()

        Profile.objects.create(user=user, phone_number=phone_number, age=age,
                               profile_picture=profile_picture, status=status, languages_known=language,gender=gender)
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
        print(user)
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
            print(other_users_data)
        return Response({'other_users_data': other_users_data})
    

class CreateChatRoom(APIView):
    def post(self, request):
        # Get the log in use
        user1 = request.user

        #second user for the chat that taking with user id
        user2_id = request.data.get('other_user_id')
        if not user2_id:
            return Response({'error':'Others user ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        #Check that the user is present in our system
        try:
            other_user_id = User.objects.get(pk=user2_id)
        except  User.DoesNotExist:
            return Response({'error':'Other user not found '}, status=status.HTTP_404_NOT_FOUND)     
        # Check that the chatroom is already created with the two user
        exixting_chat_room = ChatRoom.objects.filter(user1=user1,user2=user2_id) | ChatRoom.objects.filter(user1=user2_id, user2=user1)
        if exixting_chat_room.exists():
            return Response({'error':'Chat Room already exists'}, status=status.HTTP_400_BAD_REQUEST)
        chat_room = ChatRoom.objects.create(user1=user1,user2= user2_id)
        return  Response({'chat_room_id':chat_room.id}, status=status.HTTP_201_CREATED)
    
#for senting the message
class SendMessage(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.headers)
        # the logged user
        user1 = request.user
        other_user_id = request.data.get('other_user_id')
        message_text = request.data.get("message_text")
        if not other_user_id or not message_text:
            return Response({'error':'Others user or message text is required '}, status=status.HTTP_400_BAD_REQUEST)
        try:
            other_user =  User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            return Response({'error':'User is not found'}, status=status.HTTP_404_NOT_FOUND)
        existing_chat_room = ChatRoom.objects.filter(user1=user1, user2=other_user) |ChatRoom.objects.filter(user1=other_user, user2=user1)
        if not existing_chat_room.exists():
            # if chatroom exists and create one
            create_chat_room_view = CreateChatRoom.as_view()
            create_chat_room_request = request.clone()
            create_chat_room_request.method= 'POST'
            create_chat_room_request.data = {'other_user_id':other_user_id}
            create_chat_room_response = create_chat_room_view(create_chat_room_request)
            if create_chat_room_response.status_code != status.HTTP_201_CREATED:
                return create_chat_room_response
        
        # otherwise get chatroom for two user
        chat_room = existing_chat_room.first()
        message = Messages.objects.create(chatroom=chat_room, user=user1, text= message_text)\
        
        return Response({'message': message.id}, status=status.HTTP_201_CREATED)

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

