from rest_framework import generics, status, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, CheckoutSerializer
)


class OrderListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({
            'success': True,
            'message': 'Order created.',
            'order': OrderSerializer(order).data,
        }, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')


class OrderCancelView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status == 'canceled':
            return Response(
                {'success': False, 'error': 'Order is already canceled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status == 'paid':
            order.restore_stock_for_items()

        order.status = 'canceled'
        order.save(update_fields=['status', 'updated_at'])

        return Response({
            'success': True,
            'message': 'Order canceled successfully.',
            'order': OrderSerializer(order).data,
        })


class OrderCheckoutView(generics.GenericAPIView):
    @swagger_auto_schema(
        operation_description="Initiate payment for an order",
        request_body=CheckoutSerializer,
    )
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='pending')
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Pending order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from payments.strategy import PaymentProcessor

        provider_name = serializer.validated_data['provider']
        kwargs_extra = {}
        if 'currency' in serializer.validated_data:
            kwargs_extra['currency'] = serializer.validated_data['currency']
        if 'callback_url' in serializer.validated_data:
            kwargs_extra['callback_url'] = serializer.validated_data['callback_url']

        result = PaymentProcessor.create_payment(
            order=order,
            provider_name=provider_name,
            **kwargs_extra
        )

        if result.get('success'):
            return Response({
                'success': True,
                'message': f'Payment initiated via {provider_name}.',
                'payment_data': result,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Payment initiation failed.'),
            }, status=status.HTTP_400_BAD_REQUEST)
