from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

app_name= "guidance"

urlpatterns = [
    # Career Guidance Flow
    path("questionnaire/", views.questionnaire, name="questionnaire"),
    path("", views.home, name="home"),
    path("recommendations/", views.recommendations, name="recommendations"),
    
    # Authentication
    #path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    #path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register, name="register"),
    #path('logout/', views.auth_logout, name='logout'),
    path('logout/', LogoutView.as_view(), name='logout'),
     # Student Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("contact",views.contact_view, name="contact"),
    path("about",views.about_view, name="about")

]
