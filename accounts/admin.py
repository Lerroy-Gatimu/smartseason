from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Show the role column in the admin list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')

    # Add role to the fieldsets so it shows in the edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SmartSeason Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SmartSeason Role', {'fields': ('role',)}),
    )
