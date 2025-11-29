from django.db import models
from django.contrib.auth.models import User

class HostelBuilding(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name

class Room(models.Model):
    hostel_building = models.ForeignKey(HostelBuilding, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    capacity = models.IntegerField()
    is_ac = models.BooleanField(default=False)
    is_single = models.BooleanField(default=False)
    is_physically_challenged_friendly = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.hostel_building.name} - Room {self.room_number}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name

class HostelApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    preferred_hostel_building = models.ForeignKey(HostelBuilding, on_delete=models.CASCADE)
    preferred_room_type = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Multiple', 'Multiple')])
    requires_ac = models.BooleanField(default=False)
    requires_physically_challenged_friendly = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    allotted_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.preferred_hostel_building.name}"

class Warden(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name