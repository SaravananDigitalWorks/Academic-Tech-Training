from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name="hostel"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact,name="contact"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('register_student/', login_required(views.student_register), name='student_register'),
    path('apply/', views.apply_hostel, name='apply_hostel'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('warden/', views.warden_dashboard, name='warden_dashboard'),
    path('approve/<int:application_id>/', views.approve_application, name='approve_application'),
]