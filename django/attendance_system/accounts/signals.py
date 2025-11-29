from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Ensure related models are created
        print(f"User {instance.username} created with role {instance.role}")
