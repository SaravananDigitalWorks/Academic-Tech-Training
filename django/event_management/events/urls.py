from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home, name='home'),
    path('event/list', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/register/', views.register_event, name='register_event'),
    path('dashboard/student', views.student_dashboard, name='student_dashboard'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path('organizer/dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('organizer/event/add/', views.add_event, name='add_event'),
    path('organizer/event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('organizer/event/<int:event_id>/upload-images/', views.upload_event_images, name='upload_event_images'),
    path('organizer/event/image/<int:image_id>/delete/', views.delete_event_image, name='delete_event_image'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

]