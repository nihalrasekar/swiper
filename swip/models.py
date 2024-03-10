from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator



class Profile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=2,null=True,blank=True)
    status = models.CharField(max_length=255, blank=True)
    dailystatus_media = models.FileField(
        upload_to='dailystatus_media/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'mp4'])]
    )
    languages_known = ArrayField(models.CharField(max_length=50),null=True,blank = True)
    def user_id(self, obj):
        return obj.user.id

class ProfilePicture(models.Model):
    profile = models.ForeignKey(Profile, related_name='profile_pictures', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_pics/')

    def save(self, *args, **kwargs):
        # Check the number of existing profile pictures associated with the user
        existing_profile_pictures_count = ProfilePicture.objects.filter(profile=self.profile).count()
        
        # Ensure that the number of profile pictures does not exceed 5
        if existing_profile_pictures_count >= 5:
            raise ValueError("Maximum 5 profile pictures allowed per user.")

        # Call the superclass's save method to save the profile picture
        super().save(*args, **kwargs)



class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, on_delete = models.CASCADE,related_name = "user1_roorms")   
    user2 = models.ForeignKey(User, on_delete = models.CASCADE,related_name = "user2_roorms")  
    
class Messages(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete = models.CASCADE)  
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True) 

    

# Create your models here.
