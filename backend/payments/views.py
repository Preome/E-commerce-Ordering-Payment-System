import json
import logging
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from drf_yasg.utils import swagger_auto_schema

from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer
from .strategy import PaymentProcessor

logger = logging.getLogger('payments')


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).select_related('order')


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).select_related('order')


class PaymentVerifyView(generics.GenericAPIView):
    @swagger_auto_schema(
        operation_description="Verify a payment status with the provider",
    )
    def get(self, request, *args, **kwargs):
        payment_id = kwargs.get('pk')
        try:
            payment = Payment.objects.get(id=payment_id, order__user=request.user)
        except Payment.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        result = PaymentProcessor.verify_payment(payment.provider, payment.transaction_id)

        if result.get('verified'):
            if payment.status != 'success':
                payment.mark_success()
                payment.order.mark_paid()
                payment.order.reduce_stock_for_items()

        return Response({
            'success': True,
            'verification': result,
            'payment': PaymentSerializer(payment).data,
        })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """Stripe webhook endpoint."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    logger.info("Stripe webhook received")

    result = PaymentProcessor.process_webhook(
        'stripe',
        payload=payload.decode('utf-8') if isinstance(payload, bytes) else payload,
    )

    if sig_header:
        from payments.stripe_provider import stripe_provider
        result = stripe_provider.process_webhook(payload if isinstance(payload, (str, bytes)) else json.dumps(payload), sig_header=sig_header)

    return HttpResponse(
        json.dumps(result),
        status=200,
        content_type='application/json'
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def bkash_webhook(request):
    """bKash webhook/callback endpoint."""
    payload = request.data

    logger.info("bKash webhook received")

    result = PaymentProcessor.process_webhook('bkash', payload)

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request):
    """Manually confirm a payment after provider redirect."""
    serializer = PaymentCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    provider = serializer.validated_data['provider']
    order_id = serializer.validated_data['order_id']

    from orders.models import Order
    try:
        order = Order.objects.get(id=order_id, user=request.user, status='pending')
    except Order.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Pending order not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    payment = Payment.objects.filter(order=order, provider=provider, status='pending').first()
    if not payment:
        return Response(
            {'success': False, 'error': 'No pending payment found for this order.'},
            status=status.HTTP_404_NOT_FOUND
        )

    result = PaymentProcessor.confirm_payment(provider, payment.transaction_id)

    if result.get('success'):
        order.mark_paid()
        order.reduce_stock_for_items()
        return Response({
            'success': True,
            'message': 'Payment confirmed.',
            'order_status': order.status,
        })

    return Response({
        'success': False,
        'error': result.get('error', 'Payment confirmation failed.'),
    }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def bkash_callback(request):
    """bKash redirects here after payment. Processes callback and redirects to frontend."""
    from django.conf import settings
    payment_id = request.GET.get('paymentID') or request.POST.get('paymentID')
    payment_status = request.GET.get('status') or request.POST.get('status')

    logger.info(f"bKash callback received: paymentID={payment_id}, status={payment_status}")

    if payment_id:
        from payments.models import Payment
        payment = Payment.objects.filter(transaction_id=payment_id).first()
        if payment:
            logger.info(f"Calling confirm_payment for bKash payment {payment_id}")
            result = PaymentProcessor.confirm_payment('bkash', payment_id)
            logger.info(f"confirm_payment result: {result}")
            if not result.get('success'):
                result = PaymentProcessor.verify_payment('bkash', payment_id)
                logger.info(f"verify_payment result: {result}")
        else:
            logger.warning(f"No Payment record found for transaction_id={payment_id}")

    return HttpResponseRedirect(f'{settings.FRONTEND_URL}/orders?payment=done')
