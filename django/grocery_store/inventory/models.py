from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import *

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    groups = models.ManyToManyField(Group, related_name="inventory_users", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="inventory_users_permissions", blank=True)

    def is_superuser(self):
        return self.role and self.role.name == "Admin"

    def is_supervisor(self):
        return self.role and self.role.name == "Supervisor"

    def is_salesperson(self):
        return self.role and self.role.name == "Salesperson"

class Product(models.Model):
    name = models.CharField(max_length=255)
    grocery_type = models.CharField(max_length=100)  # Example: Dairy, Beverages
    manufacturing_date = models.DateField()
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField()

    def is_expiring_soon(self):
        return timezone.now().date() >= self.expiry_date - timedelta(days=3)

    def __str__(self):
        return f"{self.name} ({self.quantity} left)"
