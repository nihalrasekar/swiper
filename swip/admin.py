from django.contrib import admin
from django.contrib.sessions.models import Session
from .models import Profile,ProfilePicture,ChatRoom,Messages


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id','status')

    def user_id(self, obj):
        return obj.user.id
    
    user_id.short_description = 'User ID' 



    

admin.site.register(Profile,ProfileAdmin)
admin.site.register(Session)
admin.site.register(ProfilePicture)
admin.site.register(ChatRoom)
admin.site.register(Messages)
# Register your models here.
