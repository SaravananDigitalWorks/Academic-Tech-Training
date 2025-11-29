from django.urls import *
from .views import *
from django.contrib.auth import views as auth_views

app_name='inventory'

urlpatterns = [
    
    path('', index, name="home"),
    path("add/", add_product, name="add_product"),
    path("expiring/", expiring_products, name="expiring_products"),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_logout, name='logout'),
    path('list/', product_list, name='product_list'),
    path('about/', about, name='about'),
    path('contact/', contact , name='contact'),
    path("send-products/", send_expiring_products_to_telegram, name="send_products"),
]
