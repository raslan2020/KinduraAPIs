from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('register-fcm-token/', views.register_fcm_token, name='register_fcm_token'),
    path('unregister-fcm-token/<int:token_id>/', views.unregister_fcm_token, name='unregister_fcm_token'),
    path('notification-history/', views.get_notification_history, name='get_notification_history'),
    path('send-test-notification/', views.send_test_notification, name='send_test_notification'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
] 