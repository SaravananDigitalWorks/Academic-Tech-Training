from django.db import models
from django.contrib.auth.models import User, Group

class Class(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=40)
    email = models.EmailField()
    contact_number = models.CharField(max_length=10)

    def __str__(self):
        return self.name
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=40)
    email = models.EmailField()
    contact_number = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class ClassStudentMapping(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'class_name')

    def __str__(self):
        return f"{self.student} - {self.class_name}"

class ClassTeacherMapping(models.Model):    
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'class_name')

    def __str__(self):
        return f"{self.teacher} - {self.class_name}"

class Holiday(models.Model):
    date = models.DateField(unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

class Attendance(models.Model):
    SESSION_CHOICES = [
        ('M', 'Morning'),
        ('E', 'Evening'),
    ]
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    date = models.DateField()
    session = models.CharField(max_length=1, choices=SESSION_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    class Meta:
        unique_together = ('student', 'date', 'session')

    def __str__(self):
        return f"{self.student} - {self.date} - {self.session}"