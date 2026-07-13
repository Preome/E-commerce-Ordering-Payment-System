from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:pk>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
    path('<uuid:pk>/checkout/', views.OrderCheckoutView.as_view(), name='order-checkout'),
]
