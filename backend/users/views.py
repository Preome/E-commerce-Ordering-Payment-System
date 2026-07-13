from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserRegisterSerializer, UserLoginSerializer,
    UserSerializer, UserUpdateSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={201: 'User created', 400: 'Validation error'}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'success': True,
            'message': 'User registered successfully.',
            'user': UserSerializer(user).data,
            'token': token.key,
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Login with email and password",
        responses={200: 'Login success', 401: 'Invalid credentials'}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response({
                'success': False,
                'error': 'Invalid email or password.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'success': True,
            'message': 'Login successful.',
            'user': UserSerializer(user).data,
            'token': token.key,
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update current user profile",
        responses={200: 'Profile updated'}
    )
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(user, key, value)
        user.save()
        return Response({
            'success': True,
            'message': 'Profile updated.',
            'user': UserSerializer(user).data,
        })


class UserOrdersView(generics.ListAPIView):
    from orders.serializers import OrderSerializer
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.request.user.orders.prefetch_related('items__product').all()


class UserPaymentsView(generics.ListAPIView):
    from payments.serializers import PaymentSerializer
    serializer_class = PaymentSerializer

    def get_queryset(self):
        from payments.models import Payment
        return Payment.objects.filter(order__user=self.request.user).select_related('order')
