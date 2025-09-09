from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.registerview, name='register'),
    path('login/', views.loginview, name='login'),
    path('logout/', views.logoutview, name='logout'),
    path('password-forgot/', views.forgotpassword , name='password-forgot'),
    path('password-reset-sent/<str:reset_id>/', views.passwordresetsent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.passwordreset, name='reset_password'),
    
   
]
 