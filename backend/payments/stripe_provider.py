import json
import logging
import stripe

from django.conf import settings
from payments.strategy import PaymentProvider

logger = logging.getLogger('payments')


class StripePaymentProvider(PaymentProvider):
    """Stripe payment provider implementation."""

    def get_provider_name(self):
        return 'stripe'

    def _init_stripe(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment(self, order, **kwargs):
        from payments.models import PaymentManager
        self._init_stripe()

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),
                currency=kwargs.get('currency', 'usd'),
                metadata={
                    'order_id': str(order.id),
                    'user_id': str(order.user.id),
                    'user_email': order.user.email,
                },
                automatic_payment_methods={'enabled': True},
            )

            payment = PaymentManager.create_payment(
                order=order,
                provider='stripe',
                transaction_id=payment_intent.id,
                amount=order.total_amount,
                currency=kwargs.get('currency', 'usd'),
            )

            logger.info(f"Stripe payment intent created: {payment_intent.id} for order {order.id}")

            return {
                'success': True,
                'payment_id': str(payment.id),
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe create payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    def confirm_payment(self, payment_intent_id, **kwargs):
        from payments.models import PaymentManager
        self._init_stripe()

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            payment = PaymentManager.get_by_transaction_id(payment_intent_id)

            if not payment:
                return {'success': False, 'error': 'Payment record not found'}

            if payment_intent.status == 'succeeded':
                payment.mark_success(raw_response=self._serialize_intent(payment_intent))
                return {'success': True, 'status': 'success'}
            elif payment_intent.status in ('requires_payment_method', 'canceled'):
                payment.mark_failed(raw_response=self._serialize_intent(payment_intent))
                return {'success': False, 'status': payment_intent.status}

            return {'success': False, 'status': payment_intent.status}

        except stripe.error.StripeError as e:
            logger.error(f"Stripe confirm payment error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def verify_payment(self, payment_intent_id):
        from payments.models import PaymentManager
        self._init_stripe()

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            payment = PaymentManager.get_by_transaction_id(payment_intent_id)

            if payment and payment_intent.status == 'succeeded' and payment.status != 'success':
                payment.mark_success(raw_response=self._serialize_intent(payment_intent))

            return {
                'verified': payment_intent.status == 'succeeded',
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe verify payment error: {str(e)}")
            return {'verified': False, 'error': str(e)}

    def process_webhook(self, payload, sig_header=None):
        from payments.models import PaymentManager
        self._init_stripe()

        try:
            if sig_header and settings.STRIPE_WEBHOOK_SECRET:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
            else:
                event = json.loads(payload)

            event_type = event.get('type', '')
            data = event.get('data', {}).get('object', {})

            logger.info(f"Stripe webhook received: {event_type}")

            if event_type == 'payment_intent.succeeded':
                return self._handle_payment_success(data)
            elif event_type == 'payment_intent.payment_failed':
                return self._handle_payment_failure(data)
            elif event_type == 'charge.refunded':
                return self._handle_refund(data)

            return {'processed': False, 'event_type': event_type}

        except Exception as e:
            logger.error(f"Stripe webhook error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _handle_payment_success(self, data):
        from payments.models import PaymentManager
        from orders.models import Order

        payment_intent_id = data.get('id')
        payment = PaymentManager.get_by_transaction_id(payment_intent_id)
        if payment:
            payment.mark_success(raw_response=data)
            order = Order.objects.filter(id=payment.order_id).first()
            if order and order.status == 'pending':
                order.mark_paid()
                order.reduce_stock_for_items()
                logger.info(f"Order {order.id} marked as paid via Stripe webhook")
            return {'success': True, 'order_id': str(payment.order_id)}
        return {'success': False, 'error': 'Payment not found'}

    def _handle_payment_failure(self, data):
        from payments.models import PaymentManager
        payment_intent_id = data.get('id')
        payment = PaymentManager.get_by_transaction_id(payment_intent_id)
        if payment:
            payment.mark_failed(raw_response=data)
            return {'success': True, 'order_id': str(payment.order_id)}
        return {'success': False, 'error': 'Payment not found'}

    def _handle_refund(self, data):
        logger.info(f"Refund processed: {data.get('id')}")
        return {'success': True, 'type': 'refund'}

    def _serialize_intent(self, intent):
        return {
            'id': intent.id,
            'status': intent.status,
            'amount': intent.amount,
            'currency': intent.currency,
            'metadata': dict(intent.metadata) if intent.metadata else {},
        }


stripe_provider = StripePaymentProvider()
