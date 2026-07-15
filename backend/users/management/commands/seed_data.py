from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product, Category

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with admin user and sample products'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Product.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Seeding admin user...')
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin_user.set_password('admin123!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user created: admin@example.com / admin123!'))
        else:
            self.stdout.write('Admin user already exists.')

        self.stdout.write('Seeding sample user...')
        sample_user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'username': 'sampleuser',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+1234567890',
                'address': '123 Main St, City, Country',
            }
        )
        if created:
            sample_user.set_password('user123!')
            sample_user.save()
            self.stdout.write(self.style.SUCCESS(f'Sample user created: user@example.com / user123!'))

        self.stdout.write('Seeding categories...')
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Home & Kitchen', 'slug': 'home-kitchen', 'description': 'Home appliances and kitchen items'},
            {'name': 'Books', 'slug': 'books', 'description': 'Physical and digital books'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sports equipment and accessories'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = cat

        subcategories_data = [
            {'name': 'Smartphones', 'slug': 'smartphones', 'description': 'Mobile phones', 'parent': 'electronics'},
            {'name': 'Laptops', 'slug': 'laptops', 'description': 'Laptop computers', 'parent': 'electronics'},
            {'name': 'Headphones', 'slug': 'headphones', 'description': 'Audio headphones', 'parent': 'electronics'},
            {'name': 'Men\'s Wear', 'slug': 'mens-wear', 'description': 'Men clothing', 'parent': 'clothing'},
            {'name': 'Women\'s Wear', 'slug': 'womens-wear', 'description': 'Women clothing', 'parent': 'clothing'},
            {'name': 'Cookware', 'slug': 'cookware', 'description': 'Pots, pans, and cooking utensils', 'parent': 'home-kitchen'},
        ]

        for sub_data in subcategories_data:
            parent_slug = sub_data.pop('parent')
            sub, _ = Category.objects.get_or_create(
                slug=sub_data['slug'],
                defaults={**sub_data, 'parent': categories[parent_slug]}
            )
            categories[sub_data['slug']] = sub

        self.stdout.write('Seeding products...')
        products_data = [
            {'name': 'iPhone 15 Pro', 'sku': 'ELEC-001', 'description': 'Apple iPhone 15 Pro with A17 chip', 'price': 999.99, 'stock': 50, 'category': 'smartphones', 'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&h=600&fit=crop'},
            {'name': 'Samsung Galaxy S24', 'sku': 'ELEC-002', 'description': 'Samsung Galaxy S24 Ultra', 'price': 899.99, 'stock': 40, 'category': 'smartphones', 'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&h=600&fit=crop'},
            {'name': 'MacBook Pro 14"', 'sku': 'ELEC-003', 'description': 'Apple MacBook Pro 14 inch M3', 'price': 1999.99, 'stock': 25, 'category': 'laptops', 'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=600&fit=crop'},
            {'name': 'Dell XPS 15', 'sku': 'ELEC-004', 'description': 'Dell XPS 15 laptop', 'price': 1299.99, 'stock': 30, 'category': 'laptops', 'image_url': 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=800&h=600&fit=crop'},
            {'name': 'Sony WH-1000XM5', 'sku': 'ELEC-005', 'description': 'Sony noise cancelling headphones', 'price': 349.99, 'stock': 60, 'category': 'headphones', 'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop'},
            {'name': 'Classic Cotton T-Shirt', 'sku': 'CLTH-001', 'description': '100% cotton casual t-shirt', 'price': 29.99, 'stock': 200, 'category': 'mens-wear', 'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&h=600&fit=crop'},
            {'name': 'Summer Floral Dress', 'sku': 'CLTH-002', 'description': 'Lightweight floral summer dress', 'price': 59.99, 'stock': 150, 'category': 'womens-wear', 'image_url': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&h=600&fit=crop'},
            {'name': 'Non-Stick Cookware Set', 'sku': 'HOME-001', 'description': '10-piece non-stick cookware set', 'price': 149.99, 'stock': 35, 'category': 'cookware', 'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop'},
            {'name': 'Python Crash Course', 'sku': 'BOOK-001', 'description': 'Hands-on programming introduction', 'price': 39.99, 'stock': 100, 'category': 'books', 'image_url': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=600&fit=crop'},
            {'name': 'Yoga Mat Premium', 'sku': 'SPRT-001', 'description': 'Extra thick non-slip yoga mat', 'price': 49.99, 'stock': 80, 'category': 'sports', 'image_url': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=800&h=600&fit=crop'},
        ]

        count = 0
        for prod_data in products_data:
            cat_slug = prod_data.pop('category')
            _, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={**prod_data, 'category': categories.get(cat_slug)}
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete!'
            f'\n  Categories: {Category.objects.count()}'
            f'\n  Products: {Product.objects.count()} ({count} new)'
            f'\n  Admin: admin@example.com / admin123!'
            f'\n  User: user@example.com / user123!'
        ))
