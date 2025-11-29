from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    text = models.CharField(max_length=255)
    
    def __str__(self):
        return self.text
class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    criteria = models.ManyToManyField(Question, related_name="courses")

    def __str__(self):
        return self.name


class StudentResponse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.BooleanField()

    def __str__(self):
        return f"{self.student.username} - {self.question.text}: {'Yes' if self.answer else 'No'}"
