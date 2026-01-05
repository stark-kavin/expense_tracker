from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Category model for expense categorization with Material Icon support.
    Each user can have their own custom categories.
    """
    name = models.CharField(max_length=100)
    icon_name = models.CharField(
        max_length=100,
        help_text="Google Material Symbol name (e.g., 'shopping_cart', 'restaurant')"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['name', 'user']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Group(models.Model):
    """
    Group model for shared expenses among multiple users.
    """
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name='expense_groups')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def total_expenses(self):
        """Calculate total expenses for this group."""
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
    
    def member_count(self):
        """Return the number of members in the group."""
        return self.members.count()


class Expense(models.Model):
    """
    Expense model for tracking individual expenses.
    Can be personal or group-based, with optional AI generation flag.
    """
    description = models.CharField(max_length=500)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='expenses',
        help_text="Leave blank for personal expenses"
    )
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    receipt_image = models.ImageField(
        upload_to='receipts/%Y/%m/',
        blank=True,
        null=True,
        help_text="Upload receipt image"
    )
    is_ai_generated = models.BooleanField(
        default=False,
        help_text="Indicates if this expense was created via AI chat"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['paid_by', '-date']),
        ]
    
    def __str__(self):
        return f"{self.description} - ${self.amount} ({self.date})"
    
    @property
    def is_group_expense(self):
        """Check if this is a group expense."""
        return self.group is not None
