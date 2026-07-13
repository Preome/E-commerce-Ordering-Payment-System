from decimal import Decimal
from django.test import TestCase
from products.models import Product, Category


class CategoryModelTest(TestCase):
    def setUp(self):
        self.parent = Category.objects.create(
            name='Electronics', slug='electronics', description='Electronic devices'
        )
        self.child = Category.objects.create(
            name='Phones', slug='phones', description='Mobile phones', parent=self.parent
        )

    def test_category_str(self):
        self.assertEqual(str(self.parent), 'Electronics')

    def test_is_root(self):
        self.assertTrue(self.parent.is_root)
        self.assertFalse(self.child.is_root)

    def test_depth(self):
        self.assertEqual(self.parent.depth, 0)
        self.assertEqual(self.child.depth, 1)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            description='A test product',
            price=Decimal('29.99'),
            stock=100,
            status='active',
            category=self.category,
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product (SKU: TEST-001)')

    def test_is_available(self):
        self.assertTrue(self.product.is_available)

    def test_is_available_inactive(self):
        self.product.status = 'inactive'
        self.product.save()
        self.assertFalse(self.product.is_available)

    def test_is_available_out_of_stock(self):
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_available)

    def test_reduce_stock(self):
        new_stock = self.product.reduce_stock(10)
        self.assertEqual(new_stock, 90)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 90)

    def test_reduce_stock_insufficient(self):
        with self.assertRaises(ValueError):
            self.product.reduce_stock(200)

    def test_reduce_stock_negative(self):
        with self.assertRaises(ValueError):
            self.product.reduce_stock(-5)

    def test_increase_stock(self):
        new_stock = self.product.increase_stock(20)
        self.assertEqual(new_stock, 120)

    def test_sku_unique(self):
        with self.assertRaises(Exception):
            Product.objects.create(
                name='Duplicate', sku='TEST-001', price=Decimal('10.00'), stock=5
            )

    def test_product_dfs_traversal(self):
        child = Category.objects.create(name='Phones', slug='phones', parent=self.category)
        Product.objects.create(
            name='Phone', sku='PHN-001', price=Decimal('499.99'), stock=10, category=child
        )
        from products.models import CategoryHierarchy
        result = CategoryHierarchy.dfs_traverse([self.category])
        self.assertEqual(len(result), 2)


class CategoryHierarchyTest(TestCase):
    def setUp(self):
        self.root = Category.objects.create(name='Root', slug='root')
        self.child1 = Category.objects.create(name='Child1', slug='child1', parent=self.root)
        self.child2 = Category.objects.create(name='Child2', slug='child2', parent=self.root)
        self.grandchild = Category.objects.create(name='Grandchild', slug='grandchild', parent=self.child1)

        for i, cat in enumerate([self.root, self.child1, self.child2, self.grandchild]):
            Product.objects.create(
                name=f'Product {i}', sku=f'PRD-{i:03d}',
                price=Decimal('10.00'), stock=10, category=cat, status='active'
            )

    def test_dfs_traversal(self):
        from products.models import CategoryHierarchy
        result = CategoryHierarchy.dfs_traverse([self.root])
        self.assertEqual(len(result), 4)

    def test_get_related_products(self):
        from products.models import CategoryHierarchy
        related = CategoryHierarchy.get_related_products(self.child1)
        self.assertTrue(related.exists())
