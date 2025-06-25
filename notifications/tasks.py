import os
import firebase_admin
from firebase_admin import credentials, messaging
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import FCMToken, NotificationHistory
from schedules.models import CourseMedicineSchedule, CourseDayTracking


# Initialize Firebase Admin SDK
def get_firebase_app():
    """Initialize Firebase Admin SDK if not already initialized"""
    try:
        return firebase_admin.get_app()
    except ValueError:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        return firebase_admin.initialize_app(cred)


@shared_task
def send_fcm_notification(user_id, title, body, data=None, notification_type='medicine_reminder'):
    """
    Send FCM notification to a specific user
    """
    try:
        # Get Firebase app
        firebase_app = get_firebase_app()
        
        # Get user's FCM tokens
        fcm_tokens = FCMToken.objects.filter(
            user_id=user_id,
            is_active=True
        )
        
        if not fcm_tokens.exists():
            print(f"No FCM tokens found for user {user_id}")
            return False
        
        success_count = 0
        failed_count = 0
        
        for fcm_token in fcm_tokens:
            try:
                # Prepare notification message
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data or {},
                    token=fcm_token.token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            sound='default',
                            priority='high',
                            channel_id='medicine_reminders'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                badge=1
                            )
                        )
                    )
                )
                
                # Send notification
                response = messaging.send(message, app=firebase_app)
                
                # Log notification history
                NotificationHistory.objects.create(
                    user_id=user_id,
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    data=data or {},
                    fcm_response={'message_id': response}
                )
                
                success_count += 1
                print(f"FCM notification sent successfully to user {user_id}: {response}")
                
            except Exception as e:
                failed_count += 1
                print(f"Failed to send FCM notification to user {user_id}: {str(e)}")
                
                # Log failed notification
                NotificationHistory.objects.create(
                    user_id=user_id,
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    data=data or {},
                    fcm_response={'error': str(e)}
                )
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'total_count': len(fcm_tokens)
        }
        
    except Exception as e:
        print(f"Error in send_fcm_notification task: {str(e)}")
        return False


@shared_task
def send_medicine_reminder(schedule_id):
    """
    Send medicine reminder for a specific schedule
    """
    try:
        # Get the schedule
        schedule = CourseMedicineSchedule.objects.select_related('course', 'medicine').get(id=schedule_id)
        
        # Check if medicine is already taken today
        today = timezone.now().date()
        tracking_record = CourseDayTracking.objects.filter(
            course=schedule.course,
            medicine=schedule.medicine,
            date=today,
            time=schedule.time
        ).first()
        
        if tracking_record and tracking_record.taken:
            print(f"Medicine already taken for schedule {schedule_id}")
            return False
        
        # Prepare notification data
        title = "Medicine Reminder"
        body = f"It's time to take {schedule.dosage} of {schedule.medicine.name}"
        data = {
            'schedule_id': str(schedule.id),
            'medicine_id': str(schedule.medicine.id),
            'course_id': str(schedule.course.id),
            'medicine_name': schedule.medicine.name,
            'dosage': schedule.dosage,
            'time': schedule.time.strftime('%H:%M:%S'),
            'notification_type': 'medicine_reminder'
        }
        
        # Send notification
        result = send_fcm_notification.delay(
            schedule.course.user.id,
            title,
            body,
            data,
            'medicine_reminder'
        )
        
        print(f"Medicine reminder scheduled for user {schedule.course.user.id}")
        return result
        
    except CourseMedicineSchedule.DoesNotExist:
        print(f"Schedule {schedule_id} not found")
        return False
    except Exception as e:
        print(f"Error in send_medicine_reminder task: {str(e)}")
        return False


@shared_task
def schedule_medicine_reminders():
    """
    Schedule medicine reminders for all active schedules
    This task should be run periodically (e.g., every hour)
    """
    try:
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        from datetime import datetime, timedelta
        
        # Get all active schedules
        schedules = CourseMedicineSchedule.objects.filter(
            is_active=True
        ).select_related('course', 'medicine')
        
        scheduled_count = 0
        
        for schedule in schedules:
            try:
                # Calculate next reminder time
                now = timezone.now()
                schedule_time = schedule.time
                
                # Create datetime for today with the schedule time
                today_schedule = now.replace(
                    hour=schedule_time.hour,
                    minute=schedule_time.minute,
                    second=schedule_time.second,
                    microsecond=0
                )
                
                # If the time has passed today, schedule for tomorrow
                if today_schedule <= now:
                    today_schedule += timedelta(days=1)
                
                # Check if task is already scheduled
                task_name = f"medicine_reminder_{schedule.id}_{today_schedule.strftime('%Y%m%d_%H%M')}"
                
                if not PeriodicTask.objects.filter(name=task_name).exists():
                    # Create one-time task for this specific reminder
                    task = PeriodicTask.objects.create(
                        name=task_name,
                        task='notifications.tasks.send_medicine_reminder',
                        args=[schedule.id],
                        start_time=today_schedule,
                        one_off=True  # Run only once
                    )
                    
                    scheduled_count += 1
                    print(f"Scheduled medicine reminder for schedule {schedule.id} at {today_schedule}")
                
            except Exception as e:
                print(f"Error scheduling reminder for schedule {schedule.id}: {str(e)}")
        
        print(f"Scheduled {scheduled_count} medicine reminders")
        return scheduled_count
        
    except Exception as e:
        print(f"Error in schedule_medicine_reminders task: {str(e)}")
        return 0 