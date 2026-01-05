"""
Views for Expense Tracker application.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Expense, Category, Group
from .forms import ExpenseForm, CategoryForm, GroupForm, ChatExpenseForm
from .utils import process_chat_expense_input, ExpenseParseError


@login_required
def dashboard(request):
    """Main dashboard view with expense summary."""
    user = request.user
    
    # Get date range (last 30 days by default)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get user's expenses
    expenses = Expense.objects.filter(paid_by=user).select_related('category', 'group')
    recent_expenses = expenses[:10]
    
    # Calculate statistics
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    monthly_expenses = expenses.filter(
        date__gte=start_date
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Category breakdown
    category_breakdown = expenses.values(
        'category__name', 'category__icon_name'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    # Group expenses summary
    group_expenses = Group.objects.filter(
        members=user
    ).annotate(
        total=Sum('expenses__amount'),
        expense_count=Count('expenses')
    ).order_by('-total')[:5]
    
    context = {
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'recent_expenses': recent_expenses,
        'category_breakdown': category_breakdown,
        'group_expenses': group_expenses,
        'expense_count': expenses.count(),
    }
    
    return render(request, 'expenses/dashboard.html', context)


@login_required
def chat_expense(request):
    """AI chat-based expense input view."""
    form = ChatExpenseForm()
    chat_history = request.session.get('chat_history', [])
    
    if request.method == 'POST':
        form = ChatExpenseForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            
            # Add user message to history
            chat_history.append({
                'type': 'user',
                'message': user_message,
                'timestamp': datetime.now().isoformat()
            })
            
            try:
                # Process with AI
                created_expenses, success_message = process_chat_expense_input(
                    user_message, 
                    request.user
                )
                
                # Add success response to history
                chat_history.append({
                    'type': 'system',
                    'message': success_message,
                    'timestamp': datetime.now().isoformat(),
                    'expenses': [
                        {
                            'id': exp.id,
                            'description': exp.description,
                            'amount': str(exp.amount),
                            'category': exp.category.name if exp.category else None,
                            'category_icon': exp.category.icon_name if exp.category else None,
                            'group': exp.group.name if exp.group else None,
                        }
                        for exp in created_expenses
                    ]
                })
                
                messages.success(request, success_message)
                
            except ExpenseParseError as e:
                error_message = f"❌ Sorry, I couldn't process that: {str(e)}"
                chat_history.append({
                    'type': 'system',
                    'message': error_message,
                    'timestamp': datetime.now().isoformat(),
                    'is_error': True
                })
                messages.error(request, str(e))
            
            # Save chat history to session (keep last 50 messages)
            request.session['chat_history'] = chat_history[-50:]
            
            # For HTMX requests, return partial template
            if request.headers.get('HX-Request'):
                return render(request, 'expenses/partials/chat_messages.html', {
                    'chat_history': chat_history
                })
            
            # Regular request - redirect to avoid form resubmission
            return redirect('chat_expense')
    
    context = {
        'form': form,
        'chat_history': chat_history,
    }
    
    return render(request, 'expenses/chat_expense.html', context)


@login_required
def clear_chat(request):
    """Clear chat history."""
    if request.method == 'POST':
        request.session['chat_history'] = []
        messages.info(request, 'Chat history cleared')
    return redirect('chat_expense')


@login_required
def expense_list(request):
    """List all expenses with filtering options."""
    expenses = Expense.objects.filter(paid_by=request.user).select_related('category', 'group')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    # Filter by group
    group_id = request.GET.get('group')
    if group_id:
        expenses = expenses.filter(group_id=group_id)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    
    # Get filter options
    categories = Category.objects.filter(user=request.user)
    groups = Group.objects.filter(members=request.user)
    
    context = {
        'expenses': expenses,
        'categories': categories,
        'groups': groups,
        'selected_category': category_id,
        'selected_group': group_id,
    }
    
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create(request):
    """Create a new expense manually."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.paid_by = request.user
            expense.is_ai_generated = False
            expense.save()
            messages.success(request, f'Expense "{expense.description}" added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    
    context = {'form': form, 'title': 'Add Expense'}
    return render(request, 'expenses/expense_form.html', context)


@login_required
def expense_update(request, pk):
    """Update an existing expense."""
    expense = get_object_or_404(Expense, pk=pk, paid_by=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Expense "{expense.description}" updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    
    context = {'form': form, 'title': 'Edit Expense', 'expense': expense}
    return render(request, 'expenses/expense_form.html', context)


@login_required
def expense_delete(request, pk):
    """Delete an expense."""
    expense = get_object_or_404(Expense, pk=pk, paid_by=request.user)
    
    if request.method == 'POST':
        description = expense.description
        expense.delete()
        messages.success(request, f'Expense "{description}" deleted successfully!')
        return redirect('expense_list')
    
    context = {'expense': expense}
    return render(request, 'expenses/expense_confirm_delete.html', context)


@login_required
def category_list(request):
    """List all user categories."""
    categories = Category.objects.filter(user=request.user).annotate(
        expense_count=Count('expenses'),
        total_amount=Sum('expenses__amount')
    )
    
    context = {'categories': categories}
    return render(request, 'expenses/category_list.html', context)


@login_required
def category_create(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {'form': form, 'title': 'Create Category', 'icon_suggestions': CategoryForm.ICON_SUGGESTIONS}
    return render(request, 'expenses/category_form.html', context)


@login_required
def category_update(request, pk):
    """Update a category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {'form': form, 'title': 'Edit Category', 'category': category, 'icon_suggestions': CategoryForm.ICON_SUGGESTIONS}
    return render(request, 'expenses/category_form.html', context)


@login_required
def category_delete(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('category_list')
    
    context = {'category': category}
    return render(request, 'expenses/category_confirm_delete.html', context)


@login_required
def group_list(request):
    """List all user groups."""
    groups = Group.objects.filter(members=request.user).annotate(
        expense_count=Count('expenses'),
        total_amount=Sum('expenses__amount')
    ).prefetch_related('members')
    
    context = {'groups': groups}
    return render(request, 'expenses/group_list.html', context)


@login_required
def group_create(request):
    """Create a new group."""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            
            # Add creator and specified members
            group.members.add(request.user)
            for user in form.cleaned_data['members_usernames']:
                group.members.add(user)
            
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('group_list')
    else:
        form = GroupForm()
    
    context = {'form': form, 'title': 'Create Group'}
    return render(request, 'expenses/group_form.html', context)


@login_required
def group_update(request, pk):
    """Update a group."""
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            
            # Update members
            group.members.clear()
            group.members.add(request.user)
            for user in form.cleaned_data['members_usernames']:
                group.members.add(user)
            
            messages.success(request, f'Group "{group.name}" updated successfully!')
            return redirect('group_list')
    else:
        form = GroupForm(instance=group)
    
    context = {'form': form, 'title': 'Edit Group', 'group': group}
    return render(request, 'expenses/group_form.html', context)


@login_required
def group_delete(request, pk):
    """Delete a group."""
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f'Group "{name}" deleted successfully!')
        return redirect('group_list')
    
    context = {'group': group}
    return render(request, 'expenses/group_confirm_delete.html', context)


@login_required
def group_detail(request, pk):
    """View group details and expenses."""
    group = get_object_or_404(Group, pk=pk, members=request.user)
    expenses = group.expenses.all().select_related('paid_by', 'category')
    
    # Calculate per-member statistics
    member_stats = []
    for member in group.members.all():
        member_expenses = expenses.filter(paid_by=member)
        member_stats.append({
            'user': member,
            'total': member_expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
            'count': member_expenses.count()
        })
    
    context = {
        'group': group,
        'expenses': expenses,
        'member_stats': member_stats,
        'total_expenses': group.total_expenses()
    }
    
    return render(request, 'expenses/group_detail.html', context)
