import base64
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers
from .models import Profile,ChatRoom,Messages
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ['id', 'age', 'first_name', 'last_name', 'status','name','position']

    def get_status(self, profile):
        if profile.dailystatus_media:
            try:
                # Check if the media is an image
                if profile.dailystatus_media.path.endswith(('.jpg', '.jpeg', '.png')):
                    with open(profile.dailystatus_media.path, "rb") as f:
                        encoded_content = base64.b64encode(f.read()).decode("utf-8")
                    return f"data:image/jpeg;base64,{encoded_content}"
                # Check if the media is a video
                elif profile.dailystatus_media.path.endswith('.mp4'):
                    with open(profile.dailystatus_media.path, "rb") as f:
                        encoded_content = base64.b64encode(f.read()).decode("utf-8")
                    return f"data:video/mp4;base64,{encoded_content}"
                else:
                    # Unsupported media format
                    raise ImproperlyConfigured("Unsupported media format")
            except Exception as e:
                # Handle file reading errors
                raise ImproperlyConfigured(f"Error processing media file: {e}")
        return None
class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'

class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'

class ChatRoomDetailsSerializer(serializers.ModelSerializer):
    other_user_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'other_user_name', 'last_message']

    def get_other_user_name(self, obj):
        user = self.context['request'].user
        if obj.user1 == user:
            return obj.user2.username
        return obj.user1.username

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        return last_message.text if last_message else None       
    

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    
    class Meta:
        model = Messages
        fields = ['id', 'sender', 'text', 'created_at']


class SendMessageSerializer(serializers.Serializer):
    chatroom_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    message = serializers.CharField(max_length=1000)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'age', 'gender', 'status', 'languages_known', 'name']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        instance.user.first_name = user_data.get('first_name', instance.user.first_name)
        instance.user.last_name = user_data.get('last_name', instance.user.last_name)
        instance.user.email = user_data.get('email', instance.user.email)
        instance.user.save()

        instance.age = validated_data.get('age', instance.age)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.status = validated_data.get('status', instance.status)
        instance.languages_known = validated_data.get('languages_known', instance.languages_known)
        instance.name = validated_data.get('name', instance.name)


class ProfileSerializer(serializers.ModelSerializer):
    total_likes = serializers.IntegerField(source='likes', read_only=True)
    total_super_likes = serializers.IntegerField(source='super_likes.count', read_only=True)
    super_likes_by = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [ 'dailystatus_media', 'total_likes', 'total_super_likes', 'super_likes_by']

    def get_super_likes_by(self, obj):
        super_likes_users = obj.super_likes.all()
        return [user.username for user in super_likes_users]