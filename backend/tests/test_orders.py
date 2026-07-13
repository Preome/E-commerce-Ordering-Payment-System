from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from orders.models import Order, OrderItem
from products.models import Product, Category

User = get_user_model()


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='order@test.com', username='orderuser', password='pass123!'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product1 = Product.objects.create(
            name='Widget', sku='ORD-T01', price=Decimal('25.00'),
            stock=50, status='active', category=self.category
        )
        self.product2 = Product.objects.create(
            name='Gadget', sku='ORD-T02', price=Decimal('75.00'),
            stock=30, status='active', category=self.category
        )
        self.inactive_product = Product.objects.create(
            name='Old Widget', sku='ORD-T03', price=Decimal('10.00'),
            stock=5, status='inactive', category=self.category
        )

    def test_create_order(self):
        data = {
            'items': [
                {'product_id': str(self.product1.id), 'quantity': 2},
                {'product_id': str(self.product2.id), 'quantity': 1},
            ],
            'notes': 'Please ship quickly',
        }
        response = self.client.post('/api/v1/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(float(response.data['order']['total_amount']), 125.00)

    def test_create_order_insufficient_stock(self):
        data = {
            'items': [{'product_id': str(self.product1.id), 'quantity': 999}],
        }
        response = self.client.post('/api/v1/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_inactive_product(self):
        data = {
            'items': [{'product_id': str(self.inactive_product.id), 'quantity': 1}],
        }
        response = self.client.post('/api/v1/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_empty_items(self):
        data = {'items': []}
        response = self.client.post('/api/v1/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_duplicate_products(self):
        data = {
            'items': [
                {'product_id': str(self.product1.id), 'quantity': 1},
                {'product_id': str(self.product1.id), 'quantity': 2},
            ],
        }
        response = self.client.post('/api/v1/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders(self):
        Order.objects.create(user=self.user, total_amount=Decimal('50.00'))
        response = self.client.get('/api/v1/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_detail(self):
        order = Order.objects.create(user=self.user, total_amount=Decimal('50.00'))
        response = self.client.get(f'/api/v1/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_pending_order(self):
        order = Order.objects.create(user=self.user, total_amount=Decimal('50.00'), status='pending')
        response = self.client.post(f'/api/v1/orders/{order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_paid_order_restores_stock(self):
        stock_before = self.product1.stock
        order = Order.objects.create(user=self.user, total_amount=Decimal('25.00'), status='paid')
        OrderItem.objects.create(
            order=order, product=self.product1, quantity=5,
            price=self.product1.price, subtotal=self.product1.price * 5
        )
        self.product1.reduce_stock(5)
        self.product1.refresh_from_db()

        response = self.client.post(f'/api/v1/orders/{order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, stock_before)

    def test_order_unauthenticated(self):
        self.client.credentials()
        response = self.client.get('/api/v1/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CheckoutAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='checkout@test.com', username='checkout', password='pass123!'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            name='Thing', sku='CHK-001', price=Decimal('100.00'),
            stock=20, status='active', category=self.category
        )

    def _create_order(self):
        data = {
            'items': [{'product_id': str(self.product.id), 'quantity': 1}],
        }
        response = self.client.post('/api/v1/orders/', data, format='json')
        return response.data['order']['id']

    def test_checkout_stripe(self):
        order_id = self._create_order()
        data = {'provider': 'stripe', 'currency': 'usd'}
        response = self.client.post(f'/api/v1/orders/{order_id}/checkout/', data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_checkout_invalid_provider(self):
        order_id = self._create_order()
        data = {'provider': 'paypal'}
        response = self.client.post(f'/api/v1/orders/{order_id}/checkout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
