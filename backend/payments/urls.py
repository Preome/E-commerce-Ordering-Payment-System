from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<uuid:id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<uuid:pk>/verify/', views.PaymentVerifyView.as_view(), name='payment-verify'),
    path('confirm/', views.confirm_payment, name='payment-confirm'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe-webhook'),
    path('webhook/bkash/', views.bkash_webhook, name='bkash-webhook'),
    path('bkash/callback/', views.bkash_callback, name='bkash-callback'),
]
