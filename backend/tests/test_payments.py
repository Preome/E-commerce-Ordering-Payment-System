import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from payments.models import Payment
from orders.models import Order
from products.models import Product, Category

User = get_user_model()


class PaymentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='pay@test.com', username='payuser', password='pass123!'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.category = Category.objects.create(name='Stuff', slug='stuff')
        self.product = Product.objects.create(
            name='Item', sku='PAY-T01', price=Decimal('50.00'),
            stock=100, status='active', category=self.category
        )
        self.order = Order.objects.create(
            user=self.user, total_amount=Decimal('50.00'), status='pending'
        )
        self.payment = Payment.objects.create(
            order=self.order, provider='stripe',
            transaction_id='pi_test_webhook', amount=Decimal('50.00'),
        )

    def test_list_payments(self):
        response = self.client.get('/api/v1/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_detail(self):
        response = self.client.get(f'/api/v1/payments/{self.payment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stripe_webhook(self):
        webhook_data = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_webhook',
                    'status': 'succeeded',
                    'amount': 5000,
                    'currency': 'usd',
                }
            }
        }
        response = self.client.post(
            '/api/v1/payments/webhook/stripe/',
            data=json.dumps(webhook_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stripe_webhook_failure(self):
        webhook_data = {
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'id': 'pi_test_webhook',
                    'status': 'payment_failed',
                    'amount': 5000,
                    'currency': 'usd',
                }
            }
        }
        response = self.client.post(
            '/api/v1/payments/webhook/stripe/',
            data=json.dumps(webhook_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')

    def test_bkash_webhook(self):
        bkash_payment = Payment.objects.create(
            order=self.order, provider='bkash',
            transaction_id='bkash_12345', amount=Decimal('50.00'),
        )
        webhook_data = {
            'paymentID': 'bkash_12345',
            'statusCode': '0000',
            'statusMessage': 'Successful',
            'transactionStatus': 'Completed',
        }
        response = self.client.post(
            '/api/v1/payments/webhook/bkash/',
            data=webhook_data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_webhook_unknown_payment(self):
        webhook_data = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_nonexistent',
                    'status': 'succeeded',
                    'amount': 100,
                    'currency': 'usd',
                }
            }
        }
        response = self.client.post(
            '/api/v1/payments/webhook/stripe/',
            data=json.dumps(webhook_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_unauthenticated(self):
        self.client.credentials()
        response = self.client.get('/api/v1/payments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
