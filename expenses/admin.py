"""
Admin configuration for Expense Tracker models.
"""
from django.contrib import admin
from .models import Category, Group, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_name', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'icon_name']
    ordering = ['name']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']
    ordering = ['-created_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'category', 'group', 'paid_by', 'is_ai_generated', 'created_at']
    list_filter = ['date', 'category', 'group', 'is_ai_generated', 'paid_by']
    search_fields = ['description']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
