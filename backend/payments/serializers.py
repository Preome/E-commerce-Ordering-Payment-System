from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    order_total = serializers.DecimalField(source='order.total_amount', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'order_total', 'provider', 'transaction_id',
            'status', 'amount', 'currency', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    provider = serializers.ChoiceField(choices=Payment.PROVIDER_CHOICES)
    currency = serializers.CharField(max_length=3, default='USD', required=False)

    def validate_order_id(self, value):
        from orders.models import Order
        try:
            order = Order.objects.get(id=value, user=self.context['request'].user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        if order.status != 'pending':
            raise serializers.ValidationError("Order is not in pending status.")
        return value


class WebhookSerializer(serializers.Serializer):
    payload = serializers.JSONField()
