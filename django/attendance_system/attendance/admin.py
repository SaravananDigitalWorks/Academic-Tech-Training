from django.contrib import admin
from .models import Class, Student, ClassStudentMapping, Holiday, Attendance, Teacher, ClassTeacherMapping

admin.site.register(Class)
admin.site.register(Student)
admin.site.register(ClassStudentMapping)
admin.site.register(Holiday)
admin.site.register(Attendance)
admin.site.register(Teacher)
admin.site.register(ClassTeacherMapping)
