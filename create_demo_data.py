"""
Demo data creation script for Expense Tracker.
Run this after creating a superuser to populate the database with sample data.

Usage:
    python manage.py shell < create_demo_data.py

Or in Django shell:
    exec(open('create_demo_data.py').read())
"""

from django.contrib.auth.models import User
from expenses.models import Category, Group, Expense
from decimal import Decimal
from datetime import datetime, timedelta

print("=" * 50)
print("Creating Demo Data for Expense Tracker")
print("=" * 50)

# Get or create demo user
user, created = User.objects.get_or_create(
    username='demo',
    defaults={
        'email': 'demo@example.com',
        'first_name': 'Demo',
        'last_name': 'User'
    }
)
if created:
    user.set_password('demo123')
    user.save()
    print(f"✅ Created demo user: {user.username}")
else:
    print(f"ℹ️  Using existing user: {user.username}")

# Create Categories with Material Icons
categories_data = [
    ('Groceries', 'shopping_cart'),
    ('Dining Out', 'restaurant'),
    ('Transportation', 'directions_car'),
    ('Gas & Fuel', 'local_gas_station'),
    ('Entertainment', 'movie'),
    ('Health & Fitness', 'fitness_center'),
    ('Utilities', 'electric_bolt'),
    ('Shopping', 'shopping_bag'),
    ('Travel', 'flight'),
    ('Coffee & Tea', 'local_cafe'),
]

print("\n📁 Creating Categories...")
categories = {}
for name, icon in categories_data:
    cat, created = Category.objects.get_or_create(
        name=name,
        user=user,
        defaults={'icon_name': icon}
    )
    categories[name] = cat
    status = "✅ Created" if created else "ℹ️  Exists"
    print(f"   {status}: {name} ({icon})")

# Create Groups
print("\n👥 Creating Groups...")
group_data = [
    ('Weekend Trip', 'Annual camping trip with friends'),
    ('Office Team', 'Team lunch and activities'),
    ('Roommates', 'Shared apartment expenses'),
]

groups = {}
for name, desc in group_data:
    group, created = Group.objects.get_or_create(
        name=name,
        created_by=user,
        defaults={'description': desc}
    )
    if created:
        group.members.add(user)
    groups[name] = group
    status = "✅ Created" if created else "ℹ️  Exists"
    print(f"   {status}: {name}")

# Create Sample Expenses
print("\n💰 Creating Expenses...")
expenses_data = [
    # Personal expenses
    {
        'description': 'Weekly grocery shopping',
        'amount': Decimal('125.50'),
        'days_ago': 2,
        'category': 'Groceries',
        'group': None,
        'is_ai': False
    },
    {
        'description': 'Gas for car',
        'amount': Decimal('45.00'),
        'days_ago': 3,
        'category': 'Gas & Fuel',
        'group': None,
        'is_ai': True
    },
    {
        'description': 'Lunch at Italian restaurant',
        'amount': Decimal('32.75'),
        'days_ago': 1,
        'category': 'Dining Out',
        'group': None,
        'is_ai': True
    },
    {
        'description': 'Movie tickets',
        'amount': Decimal('28.00'),
        'days_ago': 5,
        'category': 'Entertainment',
        'group': None,
        'is_ai': False
    },
    {
        'description': 'Morning coffee',
        'amount': Decimal('5.50'),
        'days_ago': 0,
        'category': 'Coffee & Tea',
        'group': None,
        'is_ai': True
    },
    
    # Group expenses
    {
        'description': 'Tent for camping',
        'amount': Decimal('299.99'),
        'days_ago': 7,
        'category': 'Shopping',
        'group': 'Weekend Trip',
        'is_ai': True
    },
    {
        'description': 'Campsite reservation',
        'amount': Decimal('75.00'),
        'days_ago': 10,
        'category': 'Travel',
        'group': 'Weekend Trip',
        'is_ai': False
    },
    {
        'description': 'Team lunch buffet',
        'amount': Decimal('180.00'),
        'days_ago': 4,
        'category': 'Dining Out',
        'group': 'Office Team',
        'is_ai': True
    },
    {
        'description': 'Electricity bill',
        'amount': Decimal('95.00'),
        'days_ago': 15,
        'category': 'Utilities',
        'group': 'Roommates',
        'is_ai': False
    },
    {
        'description': 'Gym membership',
        'amount': Decimal('49.99'),
        'days_ago': 8,
        'category': 'Health & Fitness',
        'group': None,
        'is_ai': False
    },
]

expense_count = 0
for exp_data in expenses_data:
    date = datetime.now().date() - timedelta(days=exp_data['days_ago'])
    
    expense, created = Expense.objects.get_or_create(
        description=exp_data['description'],
        paid_by=user,
        defaults={
            'amount': exp_data['amount'],
            'date': date,
            'category': categories.get(exp_data['category']),
            'group': groups.get(exp_data['group']) if exp_data['group'] else None,
            'is_ai_generated': exp_data['is_ai']
        }
    )
    
    if created:
        expense_count += 1
        group_str = f" [Group: {exp_data['group']}]" if exp_data['group'] else ""
        ai_str = " [AI]" if exp_data['is_ai'] else ""
        print(f"   ✅ {exp_data['description']}: ${exp_data['amount']}{group_str}{ai_str}")

print(f"\n✨ Created {expense_count} expenses!")

# Print summary
print("\n" + "=" * 50)
print("📊 Summary")
print("=" * 50)
print(f"Categories: {Category.objects.filter(user=user).count()}")
print(f"Groups: {Group.objects.filter(members=user).count()}")
print(f"Expenses: {Expense.objects.filter(paid_by=user).count()}")

total = Expense.objects.filter(paid_by=user).aggregate(
    total=models.Sum('amount')
)['total'] or Decimal('0.00')
print(f"Total Spent: ${total}")

print("\n🎉 Demo data created successfully!")
print(f"\nLogin with:")
print(f"   Username: {user.username}")
print(f"   Password: demo123")
print("\nVisit: http://127.0.0.1:8000")
print("=" * 50)

# Fix import
from django.db import models
