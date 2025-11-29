from django.db import models
from django.contrib.auth.models import User

class ExamHall(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_per_row = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

class SubjectExamHallMapping(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_hall_mappings')
    exam_hall = models.ForeignKey(ExamHall, on_delete=models.CASCADE, related_name='subject_mappings')

    class Meta:
        unique_together = ('subject', 'exam_hall')  # Ensure no duplicate mappings

    def __str__(self):
        return f"{self.subject.name} - {self.exam_hall.name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()    

    def __str__(self):
        return self.name

class StudentSubjectMapping(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'subject')  # Ensure no duplicate mappings

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.user.username

class TeacherSubjectMapping(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject')  # Ensure no duplicate mappings

    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject.name}"

class SeatingArrangement(models.Model):
    exam_hall = models.ForeignKey(ExamHall, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()

    class Meta:
        unique_together = ('exam_hall', 'row', 'seat')  # Ensure no duplicate seats

    def __str__(self):
        return f"{self.student.name} - Row {self.row}, Seat {self.seat}"