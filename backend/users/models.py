import uuid
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from django.core.validators import EmailValidator


class UserManager(DjangoUserManager):
    def get_by_email(self, email):
        return self.filter(email__iexact=email).first()


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    is_vendor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['username'], name='idx_user_username'),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def get_my_orders(self):
        return self.orders.all()

    def get_my_payments(self):
        from payments.models import Payment
        return Payment.objects.filter(order__user=self)


class UserDAO:
    @staticmethod
    def create_user(email, username, password, **extra_fields):
        user = User.objects.create_user(
            email=email, username=username, password=password, **extra_fields
        )
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.objects.get_by_email(email)

    @staticmethod
    def get_user_by_id(user_id):
        return User.objects.filter(id=user_id).first()

    @staticmethod
    def update_user(user, **kwargs):
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user
