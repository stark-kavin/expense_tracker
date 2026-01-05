"""
Django forms for Expense Tracker application.
"""
from django import forms
from django.contrib.auth.models import User
from .models import Expense, Category, Group


class ExpenseForm(forms.ModelForm):
    """Form for manual expense entry with image upload."""
    
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'date', 'category', 'group', 'receipt_image']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter expense description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'group': forms.Select(attrs={
                'class': 'form-select'
            }),
            'receipt_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'receipt_image': 'Receipt Image (Optional)'
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Filter categories and groups to only show user's own
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['group'].queryset = Group.objects.filter(members=user)
        
        # Make category and group optional
        self.fields['category'].required = False
        self.fields['group'].required = False
        self.fields['group'].empty_label = "Personal (No Group)"


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'icon_name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Food & Dining'
            }),
            'icon_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., restaurant, shopping_cart, flight',
                'list': 'icon-suggestions'
            })
        }
        help_texts = {
            'icon_name': 'Enter a Google Material Symbol name. <a href="https://fonts.google.com/icons" target="_blank">Browse icons</a>'
        }
    
    # Common icon suggestions
    ICON_SUGGESTIONS = [
        'shopping_cart', 'restaurant', 'local_gas_station', 'flight',
        'hotel', 'medical_services', 'fitness_center', 'sports_tennis',
        'movie', 'music_note', 'book', 'school', 'computer', 'phone',
        'home', 'electric_bolt', 'water_drop', 'wifi', 'shopping_bag',
        'local_cafe', 'fastfood', 'directions_car', 'train', 'directions_bus',
        'local_taxi', 'two_wheeler', 'local_mall', 'checkroom', 'pets',
        'child_care', 'toys', 'celebration', 'cake', 'local_florist'
    ]


class GroupForm(forms.ModelForm):
    """Form for creating/editing expense groups."""
    
    members_usernames = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter usernames separated by commas (e.g., john, jane, bob)'
        }),
        help_text='Add members by username. You will be added automatically.'
    )
    
    class Meta:
        model = Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Weekend Trip, Office Team'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description for this group'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        
        # If editing existing group, pre-fill members
        if self.instance.pk:
            members = self.instance.members.exclude(pk=self.instance.created_by.pk)
            self.fields['members_usernames'].initial = ', '.join(
                [m.username for m in members]
            )
    
    def clean_members_usernames(self):
        """Validate and convert usernames to User objects."""
        usernames_str = self.cleaned_data.get('members_usernames', '')
        if not usernames_str.strip():
            return []
        
        usernames = [u.strip() for u in usernames_str.split(',') if u.strip()]
        users = []
        invalid_usernames = []
        
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                users.append(user)
            except User.DoesNotExist:
                invalid_usernames.append(username)
        
        if invalid_usernames:
            raise forms.ValidationError(
                f"These users do not exist: {', '.join(invalid_usernames)}"
            )
        
        return users


class ChatExpenseForm(forms.Form):
    """Simple form for AI chat-based expense input."""
    
    message = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Type your expense... (e.g., "Spent $50 on groceries and $30 on gas")',
            'autocomplete': 'off'
        }),
        label=''
    )
