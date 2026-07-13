from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema

from .models import Product, Category, CategoryHierarchy
from .serializers import (
    ProductSerializer, ProductCreateSerializer, ProductListSerializer,
    CategorySerializer, CategoryListSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ProductListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = Product.objects.select_related('category').all()
        category = self.request.query_params.get('category')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category:
            qs = qs.filter(category_id=category)
        if status_filter:
            if status_filter != 'all':
                qs = qs.filter(status=status_filter)
        else:
            qs = qs.filter(status='active')
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(sku__icontains=search)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        return qs.distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response({
            'success': True,
            'message': 'Product created.',
            'product': ProductSerializer(product).data,
        }, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'inactive'
        instance.save(update_fields=['status'])
        return Response({
            'success': True,
            'message': 'Product deactivated.',
        }, status=status.HTTP_200_OK)


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategoryListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Category.objects.filter(parent=None)

    def list(self, request, *args, **kwargs):
        cache_key = 'category_tree'
        tree = cache.get(cache_key)

        if tree is None:
            root_categories = self.get_queryset()
            tree_data = CategorySerializer(root_categories, many=True).data
            cache.set(cache_key, tree_data, timeout=3600)
            tree = tree_data

        return Response({'success': True, 'categories': tree})


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def perform_update(self, serializer):
        cache.delete('category_tree')
        serializer.save()

    def perform_destroy(self, instance):
        cache.delete('category_tree')
        instance.delete()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def category_hierarchy(request):
    """DFS traversal of the category tree with caching."""
    cache_key = 'category_hierarchy_dfs'
    hierarchy = cache.get(cache_key)

    if hierarchy is None:
        root_categories = Category.objects.filter(parent=None)
        traversal = CategoryHierarchy.dfs_traverse(root_categories)
        hierarchy = [
            {
                'category_id': str(item['category'].id),
                'name': item['category'].name,
                'slug': item['category'].slug,
                'depth': item['depth'],
                'product_count': item['product_count'],
            }
            for item in traversal
        ]
        cache.set(cache_key, hierarchy, timeout=3600)

    return Response({'success': True, 'hierarchy': hierarchy})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_recommendations(request, product_id):
    """Get related products via category DFS traversal."""
    cache_key = f'recommendations_{product_id}'
    recommendations = cache.get(cache_key)

    if recommendations is None:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'success': False, 'error': 'Product not found'}, status=404)

        related = CategoryHierarchy.get_related_products(product.category, limit=10)
        recommendations = ProductListSerializer(related, many=True).data
        cache.set(cache_key, recommendations, timeout=1800)

    return Response({'success': True, 'recommendations': recommendations})
