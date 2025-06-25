from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from notifications.tasks import schedule_medicine_reminders


class Command(BaseCommand):
    help = 'Set up periodic tasks for medicine reminders'

    def handle(self, *args, **options):
        try:
            # Create interval schedule for checking medicine schedules (every hour)
            interval, created = IntervalSchedule.objects.get_or_create(
                every=1,
                period=IntervalSchedule.HOURS,
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('Created interval schedule: every 1 hour')
                )
            
            # Create periodic task for scheduling medicine reminders
            task, created = PeriodicTask.objects.get_or_create(
                name='Schedule Medicine Reminders',
                defaults={
                    'task': 'notifications.tasks.schedule_medicine_reminders',
                    'interval': interval,
                    'enabled': True,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('Created periodic task: Schedule Medicine Reminders')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Periodic task already exists: Schedule Medicine Reminders')
                )
            
            # Run the task once to schedule initial reminders
            result = schedule_medicine_reminders.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Initial medicine reminders scheduled. Task ID: {result.id}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up medicine reminders: {str(e)}')
            ) 