"""
Utility functions for AI-powered expense parsing using Google Gemini API.
"""
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from google import genai
from google.genai import types
from decouple import config
from django.contrib.auth.models import User

from .models import Category, Group, Expense

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


class ExpenseParseError(Exception):
    """Custom exception for expense parsing errors."""
    pass


def get_gemini_client():
    """Get configured Gemini client instance."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured in environment variables")
    return client


def build_expense_parsing_prompt(
    user_input: str,
    user_groups: List[Dict],
    user_categories: List[Dict]
) -> str:
    """
    Build a detailed prompt for Gemini to parse expense data.
    
    Args:
        user_input: Natural language expense description
        user_groups: List of user's existing groups [{"name": "Group Name"}, ...]
        user_categories: List of user's existing categories [{"name": "Category", "icon": "icon_name"}, ...]
    
    Returns:
        Formatted prompt string
    """
    groups_str = ", ".join([g['name'] for g in user_groups]) if user_groups else "No groups"
    categories_str = ", ".join([f"{c['name']} ({c['icon']})" for c in user_categories]) if user_categories else "No categories"
    
    prompt = f"""You are an AI assistant helping to parse expense information from natural language.

User Input: "{user_input}"

Existing User Groups: {groups_str}
Existing User Categories: {categories_str}

TASK: Parse the user input and extract ALL expenses mentioned. The user might mention multiple expenses in one sentence.

For EACH expense found, extract:
1. amount (numeric value only, no currency symbols)
2. description (brief description of what was purchased)
3. category_name (match to existing categories if possible, or suggest a new category name)
4. group_name (match to existing groups if mentioned, otherwise null)
5. is_new_category (true if this is a new category not in the existing list)
6. suggested_icon (if is_new_category is true, suggest a valid Google Material Symbol icon name that fits the category)

IMPORTANT RULES:
- If multiple expenses are mentioned, return an array of expense objects
- For amounts, extract only the numeric value (e.g., "500" from "$500" or "500 rupees")
- Match group names case-insensitively to existing groups
- For categories, try to match existing ones first
- If creating a new category, suggest an appropriate Material Symbol icon name (e.g., "shopping_cart", "restaurant", "sports_tennis", "medical_services", "local_gas_station", "flight", "home", "phone", "computer", "book", "music_note", "movie", "fitness_center")
- Use today's date if no date is mentioned
- Be smart about category matching (e.g., "food" could match "Food & Dining", "groceries" could match "Groceries")

Return ONLY a valid JSON object with this exact structure:
{{
    "expenses": [
        {{
            "amount": "500.00",
            "description": "Dinner at restaurant",
            "category_name": "Food & Dining",
            "group_name": "Trekking Group",
            "is_new_category": false,
            "suggested_icon": null
        }},
        {{
            "amount": "2000.00",
            "description": "Tent purchase",
            "category_name": "Outdoor Gear",
            "group_name": "Trekking Group",
            "is_new_category": true,
            "suggested_icon": "camping"
        }}
    ]
}}

Return ONLY the JSON, no additional text or explanations."""
    
    return prompt


def parse_expense_with_gemini(
    user_input: str,
    user: User
) -> List[Dict]:
    """
    Parse natural language expense input using Gemini AI.
    
    Args:
        user_input: Natural language description of expense(s)
        user: Django User instance
    
    Returns:
        List of parsed expense dictionaries
    
    Raises:
        ExpenseParseError: If parsing fails
    """
    try:
        # Get user's existing groups and categories
        user_groups = [
            {"name": group.name}
            for group in user.expense_groups.all()
        ]
        
        user_categories = [
            {"name": cat.name, "icon": cat.icon_name}
            for cat in user.categories.all()
        ]
        
        # Build prompt
        prompt = build_expense_parsing_prompt(user_input, user_groups, user_categories)
        
        # Call Gemini API
        client = get_gemini_client()
        response = client.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=prompt
        )
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        parsed_data = json.loads(response_text)
        
        if 'expenses' not in parsed_data or not isinstance(parsed_data['expenses'], list):
            raise ExpenseParseError("Invalid response format from AI")
        
        return parsed_data['expenses']
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}\nResponse: {response_text}")
        raise ExpenseParseError(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise ExpenseParseError(f"Failed to parse expense: {str(e)}")


def create_expense_from_ai_data(
    expense_data: Dict,
    user: User,
    date: Optional[datetime] = None
) -> Expense:
    """
    Create an Expense object from AI-parsed data.
    
    Args:
        expense_data: Dictionary with parsed expense information
        user: Django User instance
        date: Optional date for the expense (defaults to today)
    
    Returns:
        Created Expense instance
    """
    # Extract data
    amount = Decimal(str(expense_data.get('amount', '0')))
    description = expense_data.get('description', 'Unnamed Expense')
    category_name = expense_data.get('category_name')
    group_name = expense_data.get('group_name')
    is_new_category = expense_data.get('is_new_category', False)
    suggested_icon = expense_data.get('suggested_icon', 'shopping_bag')
    
    if date is None:
        date = datetime.now().date()
    
    # Handle category
    category = None
    if category_name:
        if is_new_category:
            # Create new category with AI-suggested icon
            category, created = Category.objects.get_or_create(
                name=category_name,
                user=user,
                defaults={'icon_name': suggested_icon or 'category'}
            )
            if created:
                logger.info(f"Created new category: {category_name} with icon: {suggested_icon}")
        else:
            # Try to find existing category (case-insensitive)
            category = Category.objects.filter(
                name__iexact=category_name,
                user=user
            ).first()
            
            if not category:
                # Create it anyway if not found
                category = Category.objects.create(
                    name=category_name,
                    user=user,
                    icon_name=suggested_icon or 'category'
                )
    
    # Handle group
    group = None
    if group_name:
        group = Group.objects.filter(
            name__iexact=group_name,
            members=user
        ).first()
    
    # Create expense
    expense = Expense.objects.create(
        description=description,
        amount=amount,
        date=date,
        category=category,
        group=group,
        paid_by=user,
        is_ai_generated=True
    )
    
    logger.info(f"Created AI expense: {expense}")
    return expense


def process_chat_expense_input(user_input: str, user: User) -> Tuple[List[Expense], str]:
    """
    Process user's natural language input and create expense(s).
    
    Args:
        user_input: Natural language description
        user: Django User instance
    
    Returns:
        Tuple of (list of created Expense objects, success message)
    
    Raises:
        ExpenseParseError: If processing fails
    """
    # Parse with AI
    parsed_expenses = parse_expense_with_gemini(user_input, user)
    
    if not parsed_expenses:
        raise ExpenseParseError("No expenses found in the input")
    
    # Create expense objects
    created_expenses = []
    for expense_data in parsed_expenses:
        expense = create_expense_from_ai_data(expense_data, user)
        created_expenses.append(expense)
    
    # Build success message
    if len(created_expenses) == 1:
        exp = created_expenses[0]
        message = f"✅ Added expense: {exp.description} - ${exp.amount}"
        if exp.category:
            message += f" [{exp.category.name}]"
        if exp.group:
            message += f" [Group: {exp.group.name}]"
    else:
        message = f"✅ Added {len(created_expenses)} expenses:\n"
        for exp in created_expenses:
            message += f"• {exp.description} - ${exp.amount}"
            if exp.category:
                message += f" [{exp.category.name}]"
            message += "\n"
    
    return created_expenses, message
