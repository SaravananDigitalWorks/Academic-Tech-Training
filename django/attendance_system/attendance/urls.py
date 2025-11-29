from django.urls import path
from . import views
app_name = 'attendance'
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('mark_attendance/<int:class_id>/', views.mark_attendance, name='mark_attendance'),
    path('attendance_summary/<int:class_id>/', views.attendance_summary, name='attendance_summary'),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('dashboard/student', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher', views.teacher_dashboard, name='teacher_dashboard'),
    path('register_student/', views.student_register, name='student_register'),
]