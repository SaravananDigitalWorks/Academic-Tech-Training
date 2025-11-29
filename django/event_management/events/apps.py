from django.apps import AppConfig
from django.db.models.signals import post_migrate

def insert_default_roles(sender, **kwargs):
    from .models import UserRole
    default_roles = ['admin', 'organizer', 'student', 'volunteer']
    for role in default_roles:
        UserRole.objects.get_or_create(role=role)
    print("Default roles inserted successfully!")  # Debugging statement

class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

    def ready(self):
        print("AppConfig.ready() called!")  # Debugging statement
        # Connect the signal to insert default roles after migrations
        post_migrate.connect(insert_default_roles, sender=self)