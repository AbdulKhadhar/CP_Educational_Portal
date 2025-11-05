# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, College

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_email', 'established_year']
    search_fields = ['name', 'code', 'contact_email']
    list_filter = ['established_year']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'college', 'is_staff']
    list_filter = ['role', 'college', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'college', 'phone', 'profile_picture', 'date_of_birth')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'college', 'phone')}),
    )