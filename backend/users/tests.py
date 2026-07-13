from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123!',
            first_name='Test',
            last_name='User',
            phone='+1234567890',
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123!'))
        self.assertFalse(self.user.is_vendor)
        self.assertIsNotNone(self.user.id)

    def test_email_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                username='other',
                password='pass123!',
            )

    def test_user_str(self):
        self.assertEqual(str(self.user), 'test@example.com (Test User)')

    def test_get_by_email(self):
        found = User.objects.get_by_email('TEST@EXAMPLE.COM')
        self.assertEqual(found.id, self.user.id)

    def test_user_dao_create(self):
        from users.models import UserDAO
        user = UserDAO.create_user(
            email='dao@example.com',
            username='daouser',
            password='daopass123!',
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'dao@example.com')

    def test_user_dao_get_by_id(self):
        from users.models import UserDAO
        found = UserDAO.get_user_by_id(self.user.id)
        self.assertEqual(found.email, self.user.email)

    def test_user_dao_update(self):
        from users.models import UserDAO
        updated = UserDAO.update_user(self.user, phone='+9876543210')
        self.assertEqual(updated.phone, '+9876543210')

    def test_get_my_orders(self):
        self.assertEqual(self.user.get_my_orders().count(), 0)
