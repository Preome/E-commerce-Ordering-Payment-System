from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.models import Product, Category

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='order@example.com', username='orderuser', password='pass123!'
        )
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product1 = Product.objects.create(
            name='Product 1', sku='ORD-001', price=Decimal('25.00'),
            stock=50, status='active', category=self.category
        )
        self.product2 = Product.objects.create(
            name='Product 2', sku='ORD-002', price=Decimal('40.00'),
            stock=30, status='active', category=self.category
        )
        self.order = Order.objects.create(user=self.user, status='pending')
        self.item1 = OrderItem.objects.create(
            order=self.order, product=self.product1,
            quantity=2, price=self.product1.price,
            subtotal=self.product1.price * 2
        )
        self.item2 = OrderItem.objects.create(
            order=self.order, product=self.product2,
            quantity=1, price=self.product2.price,
            subtotal=self.product2.price * 1
        )

    def test_order_str(self):
        self.assertIn(str(self.order.id)[:8], str(self.order))

    def test_calculate_total(self):
        total = self.order.calculate_total()
        self.assertEqual(total, Decimal('90.00'))
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal('90.00'))

    def test_mark_paid(self):
        self.order.mark_paid()
        self.assertEqual(self.order.status, 'paid')

    def test_mark_canceled(self):
        self.order.mark_canceled()
        self.assertEqual(self.order.status, 'canceled')

    def test_reduce_stock_for_items(self):
        self.order.reduce_stock_for_items()
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 48)
        self.assertEqual(self.product2.stock, 29)

    def test_restore_stock_for_items(self):
        self.order.reduce_stock_for_items()
        self.order.restore_stock_for_items()
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 50)
        self.assertEqual(self.product2.stock, 30)

    def test_order_item_subtotal(self):
        self.assertEqual(self.item1.subtotal, Decimal('50.00'))
        self.assertEqual(self.item2.subtotal, Decimal('40.00'))


class OrderManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='mgr@example.com', username='mgruser', password='pass123!'
        )
        self.category = Category.objects.create(name='Books', slug='books')
        self.product = Product.objects.create(
            name='Book', sku='BOK-001', price=Decimal('15.00'),
            stock=100, status='active', category=self.category
        )

    def test_create_order(self):
        from orders.models import OrderManager
        order = OrderManager.create_order(
            self.user,
            [{'product': self.product, 'quantity': 3}]
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, Decimal('45.00'))

    def test_get_user_orders(self):
        Order.objects.create(user=self.user)
        from orders.models import OrderManager
        orders = OrderManager.get_user_orders(self.user)
        self.assertEqual(orders.count(), 1)
