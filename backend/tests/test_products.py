from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from products.models import Product, Category

User = get_user_model()


class ProductAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email='admin@test.com', username='admin', password='admin123!'
        )
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='user123!'
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Test Product', sku='TST-001', price=Decimal('49.99'),
            stock=100, status='active', category=self.category
        )

    def test_list_products(self):
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_detail(self):
        response = self.client.get(f'/api/v1/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        data = {
            'name': 'New Product', 'sku': 'NEW-001', 'price': '29.99', 'stock': 50,
            'category': str(self.category.id),
        }
        response = self.client.post('/api/v1/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_non_admin_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        data = {
            'name': 'Forbidden', 'sku': 'FOR-001', 'price': '10.00', 'stock': 5,
        }
        response = self.client.post('/api/v1/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_duplicate_sku(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        data = {
            'name': 'Dup', 'sku': 'TST-001', 'price': '10.00', 'stock': 5,
        }
        response = self.client.post('/api/v1/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.patch(
            f'/api/v1/products/{self.product.id}/',
            {'price': '59.99'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_product_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.delete(f'/api/v1/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, 'inactive')

    def test_product_search(self):
        response = self.client.get('/api/v1/products/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_filter_by_category(self):
        response = self.client.get(f'/api/v1/products/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_list(self):
        response = self.client.get('/api/v1/products/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_hierarchy(self):
        response = self.client.get('/api/v1/products/categories/hierarchy/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_recommendations(self):
        response = self.client.get(f'/api/v1/products/{self.product.id}/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
