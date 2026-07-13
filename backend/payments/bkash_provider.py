import json
import logging
import requests

from django.conf import settings
from payments.strategy import PaymentProvider

logger = logging.getLogger('payments')


class BKashPaymentProvider(PaymentProvider):
    """bKash payment provider implementation (Checkout URL Based v1.2.0-beta)."""

    def __init__(self):
        self._token = None

    def get_provider_name(self):
        return 'bkash'

    def _get_token(self):
        try:
            url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/token/grant"
            payload = {
                "app_key": settings.BKASH_APP_KEY,
                "app_secret": settings.BKASH_APP_SECRET,
            }
            headers = {
                "username": settings.BKASH_USERNAME,
                "password": settings.BKASH_PASSWORD,
                "Content-Type": "application/json",
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()

            if data.get('id_token'):
                self._token = data['id_token']
                logger.info("bKash token granted successfully")
                return self._token
            else:
                logger.error(f"bKash token error: {data}")
                return None

        except requests.RequestException as e:
            logger.error(f"bKash token request failed: {str(e)}")
            return None

    def _get_headers(self):
        if not self._token:
            self._get_token()
        return {
            "Authorization": f"Bearer {self._token}",
            "X-App-Key": settings.BKASH_APP_KEY,
            "Content-Type": "application/json",
        }

    def create_payment(self, order, **kwargs):
        from payments.models import PaymentManager

        try:
            url = settings.BKASH_CHECKOUT_URL
            callback_base = f"{settings.BACKEND_URL}/api/v1/payments/bkash/callback"
            payload = {
                "mode": "0011",
                "payerReference": order.user.email or "guest",
                "callbackURL": callback_base,
                "amount": str(order.total_amount),
                "currency": "BDT",
                "intent": "sale",
                "merchantInvoiceNumber": f"INV-{str(order.id)[:8]}",
            }

            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            data = response.json()

            if data.get('paymentID'):
                payment = PaymentManager.create_payment(
                    order=order,
                    provider='bkash',
                    transaction_id=data['paymentID'],
                    amount=order.total_amount,
                    currency='BDT',
                )

                logger.info(f"bKash payment created: {data['paymentID']} for order {order.id}")

                return {
                    'success': True,
                    'payment_id': str(payment.id),
                    'bkash_payment_id': data['paymentID'],
                    'bkash_url': data.get('bkashURL'),
                    'status_message': data.get('statusMessage', ''),
                }
            else:
                logger.error(f"bKash create payment error: {data}")
                return {
                    'success': False,
                    'error': data.get('errorMessage', data.get('statusMessage', 'Payment creation failed')),
                    'status_code': data.get('statusCode'),
                }

        except requests.RequestException as e:
            logger.error(f"bKash create payment request failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def confirm_payment(self, bkash_payment_id, **kwargs):
        from payments.models import PaymentManager

        try:
            url = settings.BKASH_EXECUTE_URL
            payload = {"paymentID": bkash_payment_id}

            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            data = response.json()

            payment = PaymentManager.get_by_transaction_id(bkash_payment_id)

            if not payment:
                return {'success': False, 'error': 'Payment record not found'}

            if data.get('statusCode') == '0000':
                payment.mark_success(raw_response=data)
                order = payment.order
                if order.status == 'pending':
                    order.mark_paid()
                    order.reduce_stock_for_items()
                return {'success': True, 'status': 'success', 'data': data}
            else:
                payment.mark_failed(raw_response=data)
                return {'success': False, 'status': 'failed', 'error': data.get('statusMessage')}

        except requests.RequestException as e:
            logger.error(f"bKash confirm payment request failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def verify_payment(self, bkash_payment_id):
        from payments.models import PaymentManager

        try:
            url = settings.BKASH_QUERY_URL
            payload = {"paymentID": bkash_payment_id}

            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            data = response.json()

            payment = PaymentManager.get_by_transaction_id(bkash_payment_id)
            if payment and data.get('statusCode') == '0000' and payment.status != 'success':
                payment.mark_success(raw_response=data)

            verified = (
                data.get('statusCode') == '0000' and
                data.get('transactionStatus') == 'Completed'
            )

            return {
                'verified': verified,
                'status': data.get('transactionStatus'),
                'amount': data.get('amount'),
            }

        except requests.RequestException as e:
            logger.error(f"bKash verify payment request failed: {str(e)}")
            return {'verified': False, 'error': str(e)}

    def process_webhook(self, payload):
        from payments.models import PaymentManager

        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
            bkash_payment_id = data.get('paymentID')

            logger.info(f"bKash webhook received for: {bkash_payment_id}")

            if data.get('statusMessage') == 'Successful' or data.get('statusCode') == '0000':
                return self.confirm_payment(bkash_payment_id)
            else:
                payment = PaymentManager.get_by_transaction_id(bkash_payment_id)
                if payment:
                    payment.mark_failed(raw_response=data)
                return {'success': False, 'status': 'failed'}

        except Exception as e:
            logger.error(f"bKash webhook error: {str(e)}")
            return {'success': False, 'error': str(e)}


bkash_provider = BKashPaymentProvider()
