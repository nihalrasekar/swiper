import base64
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ['id', 'age', 'first_name', 'last_name', 'status']

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
