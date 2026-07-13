from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_vendor', 'is_staff', 'created_at')
    list_filter = ('is_vendor', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra', {'fields': ('phone', 'address', 'is_vendor', 'created_at', 'updated_at')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Extra', {'fields': ('email', 'phone', 'address')}),
    )
