from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
from django.conf import settings

def upload_to_event_images(instance, filename):
    # Generate a unique filename using timestamp
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    ext = os.path.splitext(filename)[1]  # Get the file extension
    new_filename = f"{timestamp}{ext}"  # Combine timestamp and extension
    return os.path.join('event_images', new_filename)  # Save in 'event_images' folder

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('student', 'Student'),
        ('volunteer', 'Volunteer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.role

class UserRoleMapping(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.role.role}"

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class EventDate(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_dates')
    date = models.DateField()

    def __str__(self):
        return f"{self.event.name} - {self.date}"

class Agenda(models.Model):
    event_date = models.ForeignKey(EventDate, on_delete=models.CASCADE, related_name='agendas')
    title = models.CharField(max_length=255)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.event_date.event.name} - {self.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['event_date', 'start_time', 'end_time'],
                name='unique_agenda_slot'
            )
        ]

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_events')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=upload_to_event_images)

    def __str__(self):
        return f"{self.event.name} - Image"
    
    def delete(self, *args, **kwargs):
        # Delete the physical file from the filesystem
        if self.image:
            file_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            if os.path.exists(file_path):
                os.remove(file_path)
        # Call the parent class's delete method
        super().delete(*args, **kwargs)
        