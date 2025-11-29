from django.contrib import admin
from .models import Question, Course, StudentResponse

admin.site.register(Question)
admin.site.register(Course)
admin.site.register(StudentResponse)

