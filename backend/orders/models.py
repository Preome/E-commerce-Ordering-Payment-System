import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders'
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_order_user_status'),
            models.Index(fields=['status'], name='idx_order_status'),
            models.Index(fields=['created_at'], name='idx_order_created'),
        ]

    def __str__(self):
        return f"Order {str(self.id)[:8]}... by {self.user.email} - {self.status}"

    def calculate_total(self):
        total = Decimal('0.00')
        for item in self.items.select_related('product').all():
            total += item.subtotal
        self.total_amount = total
        self.save(update_fields=['total_amount', 'updated_at'])
        return self.total_amount

    def mark_paid(self):
        self.status = 'paid'
        self.save(update_fields=['status', 'updated_at'])

    def mark_canceled(self):
        self.status = 'canceled'
        self.save(update_fields=['status', 'updated_at'])

    def reduce_stock_for_items(self):
        for item in self.items.select_related('product').all():
            item.product.reduce_stock(item.quantity)

    def restore_stock_for_items(self):
        for item in self.items.select_related('product').all():
            item.product.increase_stock(item.quantity)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        unique_together = ['order', 'product']
        indexes = [
            models.Index(fields=['order'], name='idx_orderitem_order'),
            models.Index(fields=['product'], name='idx_orderitem_product'),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {str(self.order.id)[:8]}..."

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderManager:
    @staticmethod
    def create_order(user, items_data):
        order = Order.objects.create(user=user)
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
                subtotal=product.price * quantity,
            )
        order.calculate_total()
        return order

    @staticmethod
    def get_user_orders(user):
        return Order.objects.filter(user=user).prefetch_related('items__product')

    @staticmethod
    def get_order_with_items(order_id, user=None):
        from django.shortcuts import get_object_or_404
        qs = Order.objects.prefetch_related('items__product')
        if user:
            return get_object_or_404(qs, id=order_id, user=user)
        return get_object_or_404(qs, id=order_id)

    @staticmethod
    def cancel_order(order):
        if order.status == 'paid':
            order.restore_stock_for_items()
        order.mark_canceled()
        return order
