from django.urls import path
from . import views
app_name = 'seating'

urlpatterns = [
    path("", views.home, name="home"),
    path('about/', views.about, name='about'),
     path('contact/', views.contact, name='contact'),
    path('add-student/', views.add_student, name='add_student'),
    path('student-list/', views.student_list, name='student_list'),
    path('add-student-subject-mapping/', views.add_student_subject_mapping, name='add_student_subject_mapping'),
    path('student-subject-mapping-list/', views.student_subject_mapping_list, name='student_subject_mapping_list'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('teacher-list/', views.teacher_list, name='teacher_list'),
    path('add-teacher-subject-mapping/', views.add_teacher_subject_mapping, name='add_teacher_subject_mapping'),
    path('teacher-subject-mapping-list/', views.teacher_subject_mapping_list, name='teacher_subject_mapping_list'),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("dashboard/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    #path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path('map_seating/', views.map_seating, name='map_seating'),
]
