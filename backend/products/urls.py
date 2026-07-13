from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/hierarchy/', views.category_hierarchy, name='category-hierarchy'),
    path('<uuid:product_id>/recommendations/', views.product_recommendations, name='product-recommendations'),
]
