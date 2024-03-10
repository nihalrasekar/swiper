from django.urls import path
from django.conf.urls.static import static
from.views import TokenView,UserRegistration,OptionsMatches,SendMessage,DailyStatusMediaUpload
from django.conf import settings

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='user-registration'),
    path('token/',TokenView.as_view(),name='token-request'),
    path('optionsmatches/',OptionsMatches.as_view(),name='all matches'),
    path('send-message/', SendMessage.as_view(), name='send_message'),
    path('upload-daily-status/', DailyStatusMediaUpload.as_view(), name='upload_daily_status'),
    # Add other URLs as needed
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)