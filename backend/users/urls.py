from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('my-orders/', views.UserOrdersView.as_view(), name='user-orders'),
    path('my-payments/', views.UserPaymentsView.as_view(), name='user-payments'),
]
