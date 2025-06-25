from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import JsonResponse
from .models import FCMToken, NotificationHistory
from .tasks import send_fcm_notification
from utils.response_utils import success_response, error_response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_fcm_token(request):
    """
    Register FCM token for the authenticated user
    """
    try:
        data = request.data
        
        # Validate required fields
        if 'token' not in data:
            return error_response("Missing 'token' field", status.HTTP_400_BAD_REQUEST)
        
        token = data['token']
        device_type = data.get('device_type', 'web')
        
        # Check if token already exists
        existing_token = FCMToken.objects.filter(token=token).first()
        
        if existing_token:
            # Update existing token
            existing_token.user = request.user
            existing_token.device_type = device_type
            existing_token.is_active = True
            existing_token.save()
            
            return success_response({
                'message': 'FCM token updated successfully',
                'token_id': existing_token.id
            })
        else:
            # Create new token
            fcm_token = FCMToken.objects.create(
                user=request.user,
                token=token,
                device_type=device_type
            )
            
            return success_response({
                'message': 'FCM token registered successfully',
                'token_id': fcm_token.id
            }, status_code=status.HTTP_201_CREATED)
            
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unregister_fcm_token(request, token_id):
    """
    Unregister FCM token for the authenticated user
    """
    try:
        # Get the token
        fcm_token = FCMToken.objects.filter(
            id=token_id,
            user=request.user
        ).first()
        
        if not fcm_token:
            return error_response("FCM token not found", status.HTTP_404_NOT_FOUND)
        
        # Deactivate the token
        fcm_token.is_active = False
        fcm_token.save()
        
        return success_response({
            'message': 'FCM token unregistered successfully'
        })
        
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_history(request):
    """
    Get notification history for the authenticated user
    """
    try:
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Get notifications
        notifications = NotificationHistory.objects.filter(
            user=request.user
        ).order_by('-sent_at')
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        notifications_page = notifications[start:end]
        
        # Prepare response data
        notification_data = []
        for notification in notifications_page:
            notification_data.append({
                'id': notification.id,
                'title': notification.title,
                'body': notification.body,
                'notification_type': notification.notification_type,
                'data': notification.data,
                'sent_at': notification.sent_at,
                'is_read': notification.is_read,
                'fcm_response': notification.fcm_response
            })
        
        return success_response({
            'notifications': notification_data,
            'total_count': notifications.count(),
            'page': page,
            'page_size': page_size,
            'has_next': notifications.count() > end
        })
        
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_notification(request):
    """
    Send a test notification to the authenticated user
    """
    try:
        data = request.data
        
        title = data.get('title', 'Test Notification')
        body = data.get('body', 'This is a test notification')
        
        # Send notification asynchronously
        result = send_fcm_notification.delay(
            request.user.id,
            title,
            body,
            data.get('data', {}),
            'test'
        )
        
        return success_response({
            'message': 'Test notification sent successfully',
            'task_id': result.id
        })
        
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read
    """
    try:
        # Get the notification
        notification = NotificationHistory.objects.filter(
            id=notification_id,
            user=request.user
        ).first()
        
        if not notification:
            return error_response("Notification not found", status.HTTP_404_NOT_FOUND)
        
        # Mark as read
        notification.is_read = True
        notification.save()
        
        return success_response({
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR) 