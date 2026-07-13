from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'total_amount', 'status', 'items', 'item_count', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_amount', 'status', 'created_at', 'updated_at']

    def get_item_count(self, obj):
        return obj.items.count()


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, status='active')
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True, min_length=1)
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_items(self, value):
        product_ids = [item['product_id'] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products in the order.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        order = Order.objects.create(user=user, notes=validated_data.get('notes', ''))

        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            if product.stock < item_data['quantity']:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.stock}"
                )
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price,
                subtotal=product.price * item_data['quantity'],
            )

        order.calculate_total()
        return order


class CheckoutSerializer(serializers.Serializer):
    PROVIDER_CHOICES = [('stripe', 'Stripe'), ('bkash', 'bKash')]
    provider = serializers.ChoiceField(choices=PROVIDER_CHOICES)
    currency = serializers.CharField(max_length=3, default='usd', required=False)
    callback_url = serializers.URLField(required=False, allow_blank=True)
