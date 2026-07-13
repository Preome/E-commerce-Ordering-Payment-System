from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children', 'product_count', 'created_at']

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data

    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class CategoryListSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    is_available = serializers.BooleanField(read_only=True)
    image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'price', 'stock',
            'status', 'category', 'category_name', 'image_url',
            'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'price', 'stock', 'status', 'category', 'image_url']

    def validate_sku(self, value):
        instance = self.instance
        qs = Product.objects.filter(sku=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)

    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'stock', 'status', 'category', 'category_name', 'image_url']
