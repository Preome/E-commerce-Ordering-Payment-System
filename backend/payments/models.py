import uuid
from django.db import models
from django.conf import settings


class Payment(models.Model):
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('bkash', 'bKash'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE, related_name='payments'
    )
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order'], name='idx_payment_order'),
            models.Index(fields=['transaction_id'], name='idx_payment_txn'),
            models.Index(fields=['provider', 'status'], name='idx_payment_provider_status'),
        ]

    def __str__(self):
        return f"Payment {self.provider} - {self.transaction_id[:20]}... ({self.status})"

    def mark_success(self, raw_response=None):
        self.status = 'success'
        if raw_response:
            self.raw_response = raw_response
        self.save(update_fields=['status', 'raw_response', 'updated_at'])

    def mark_failed(self, raw_response=None):
        self.status = 'failed'
        if raw_response:
            self.raw_response = raw_response
        self.save(update_fields=['status', 'raw_response', 'updated_at'])


class PaymentManager:
    @staticmethod
    def create_payment(order, provider, transaction_id, amount, currency='USD'):
        return Payment.objects.create(
            order=order,
            provider=provider,
            transaction_id=transaction_id,
            amount=amount,
            currency=currency,
        )

    @staticmethod
    def get_by_transaction_id(transaction_id):
        return Payment.objects.filter(transaction_id=transaction_id).first()

    @staticmethod
    def get_user_payments(user):
        return Payment.objects.filter(order__user=user).select_related('order')
