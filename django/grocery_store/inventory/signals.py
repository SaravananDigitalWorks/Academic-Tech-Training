from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role

@receiver(post_migrate)
def create_roles(sender, **kwargs):
    if sender.name == "inventory":
        roles = ["Admin", "Supervisor", "Salesperson"]
        for role in roles:
            Role.objects.get_or_create(name=role)
