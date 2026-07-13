from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from payments.models import Payment
from orders.models import Order
from products.models import Product, Category

User = get_user_model()


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='pay@example.com', username='payuser', password='pass123!'
        )
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Gadget', sku='PAY-001', price=Decimal('99.99'),
            stock=10, status='active', category=self.category
        )
        self.order = Order.objects.create(user=self.user, total_amount=Decimal('99.99'), status='pending')
        self.payment = Payment.objects.create(
            order=self.order,
            provider='stripe',
            transaction_id='pi_test_12345',
            amount=Decimal('99.99'),
            currency='USD',
        )

    def test_payment_str(self):
        self.assertIn('stripe', str(self.payment))
        self.assertIn('pi_test_12345', str(self.payment))

    def test_mark_success(self):
        self.payment.mark_success(raw_response={'status': 'succeeded'})
        self.assertEqual(self.payment.status, 'success')
        self.assertEqual(self.payment.raw_response, {'status': 'succeeded'})

    def test_mark_failed(self):
        self.payment.mark_failed(raw_response={'error': 'card declined'})
        self.assertEqual(self.payment.status, 'failed')

    def test_transaction_id_unique(self):
        with self.assertRaises(Exception):
            Payment.objects.create(
                order=self.order,
                provider='bkash',
                transaction_id='pi_test_12345',
                amount=Decimal('99.99'),
            )


class PaymentProcessorTest(TestCase):
    def test_available_providers(self):
        from payments.strategy import PaymentProcessor
        providers = PaymentProcessor.available_providers()
        self.assertIn('stripe', providers)
        self.assertIn('bkash', providers)

    def test_get_provider(self):
        from payments.strategy import PaymentProcessor
        provider = PaymentProcessor.get_provider('stripe')
        self.assertEqual(provider.get_provider_name(), 'stripe')

    def test_get_unknown_provider(self):
        from payments.strategy import PaymentProcessor
        with self.assertRaises(ValueError):
            PaymentProcessor.get_provider('paypal')
