import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        indexes = [
            models.Index(fields=['slug'], name='idx_category_slug'),
            models.Index(fields=['parent'], name='idx_category_parent'),
        ]

    def __str__(self):
        return self.name

    @property
    def is_root(self):
        return self.parent is None

    @property
    def depth(self):
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level


class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    image_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['sku'], name='idx_product_sku'),
            models.Index(fields=['status'], name='idx_product_status'),
            models.Index(fields=['category'], name='idx_product_category'),
            models.Index(fields=['price'], name='idx_product_price'),
        ]

    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"

    @property
    def is_available(self):
        return self.status == 'active' and self.stock > 0

    def reduce_stock(self, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.stock < quantity:
            raise ValueError(f"Insufficient stock for {self.name}. Available: {self.stock}")
        self.stock -= quantity
        self.save(update_fields=['stock', 'updated_at'])
        return self.stock

    def increase_stock(self, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.stock += quantity
        self.save(update_fields=['stock', 'updated_at'])
        return self.stock


class CategoryHierarchy:
    @staticmethod
    def dfs_traverse(root_categories):
        result = []

        def _dfs(category, depth=0):
            result.append({
                'category': category,
                'depth': depth,
                'product_count': category.products.count(),
            })
            for child in category.children.all():
                _dfs(child, depth + 1)

        for root in root_categories:
            _dfs(root)
        return result

    @staticmethod
    def get_related_products(category, limit=10):
        related = Product.objects.filter(
            category__in=CategoryHierarchy._get_ancestors_and_descendants(category),
            status='active'
        ).exclude(
            category=category
        ).distinct()[:limit]
        return related

    @staticmethod
    def _get_ancestors_and_descendants(category):
        categories = set()
        current = category
        while current:
            categories.add(current)
            current = current.parent
        CategoryHierarchy._add_descendants(category, categories)
        return categories

    @staticmethod
    def _add_descendants(category, result_set):
        for child in category.children.all():
            result_set.add(child)
            CategoryHierarchy._add_descendants(child, result_set)
