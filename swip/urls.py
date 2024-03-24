from django.urls import path
from django.conf.urls.static import static
from.views import TokenView,UserRegistration,OptionsMatches,SendMessage,DailyStatusMediaUpload,UserChatRooms, SendMessageToChatRoom,LikeSuperLikeView,UserProfileView,ProfileView
from django.conf import settings

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='user-registration'),
    path('token/',TokenView.as_view(),name='token-request'),
    path('optionsmatches/',OptionsMatches.as_view(),name='all matches'),
     #path('create-chat-room/', CreateChatRoom.as_view(), name='create_chat_room'),
    path('send-message/', SendMessage.as_view(), name='send_message'),
    path('upload-daily-status/', DailyStatusMediaUpload.as_view(), name='upload_daily_status'),
    path('user-chat-rooms/', UserChatRooms.as_view(), name='user_chat_rooms'),
    #path('chat-room-messages/<int:chat_id>/', ChatRoomMessages.as_view(), name='chat_room_messages'),
    path('send-message/', SendMessageToChatRoom.as_view(), name='send_message_to_chat_room'),
    path('profiles/<int:profile_id>/like-super-like/', LikeSuperLikeView.as_view()),
    path('user-profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # Add other URLs as needed
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)