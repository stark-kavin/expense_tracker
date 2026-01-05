# Django Expense Tracker with AI Integration

A robust expense tracking web application built with Django, featuring AI-powered natural language expense input using Google's Gemini API.

## Features

### 🤖 AI-Powered Expense Input
- Natural language processing for expense entries
- Automatic categorization with Material Icon suggestions
- Support for multiple expenses in one sentence
- Group expense detection and matching

### 💰 Expense Management
- Manual and AI-based expense entry
- Receipt image uploads
- Category and group organization
- Advanced filtering and search

### 👥 Group Expenses
- Create and manage expense groups
- Track shared expenses across multiple users
- Per-member expense breakdowns
- Group dashboards with statistics

### 🎨 Modern UI/UX
- Bootstrap 5 responsive design
- Google Material Symbols icons
- HTMX for smooth interactions
- Mobile-friendly interface

## Tech Stack

- **Backend:** Python 3.13, Django 5.2
- **Database:** SQLite (Development)
- **AI:** Google Gemini API (google-generativeai)
- **Frontend:** Django Templates, Bootstrap 5, HTMX
- **Icons:** Google Material Symbols (Outlined)

## Installation

### Prerequisites
- Python 3.12 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup Steps

1. **Clone and navigate to the project**
   ```bash
   cd c:\Users\Kavin\Documents\expense_tracker
   ```

2. **Virtual environment is already created (.venv)**
   - Activate it:
     ```bash
     .venv\Scripts\activate
     ```

3. **Install dependencies (already installed)**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_gemini_api_key_here
     SECRET_KEY=your_django_secret_key_here
     DEBUG=True
     ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open browser to: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## Usage

### AI Chat Expense Entry

Navigate to the "AI Chat" page and type natural language expenses:

**Examples:**
- "I spent $50 on groceries"
- "Bought lunch for $25 and coffee for $5"
- "Spent 500 on dinner with the trekking group and 2000 on tent"
- "Gas $40, parking $10 for road trip group"

The AI will:
1. Parse multiple expenses from one sentence
2. Auto-detect categories (or create new ones)
3. Match group names to existing groups
4. Suggest appropriate Material Icons for new categories

### Manual Entry

Use the "Add Expense" button for traditional form-based entry with:
- Description, amount, date
- Category selection
- Group selection (optional)
- Receipt image upload

### Categories

Categories include a **Material Symbol icon name** (e.g., `shopping_cart`, `restaurant`).

**Browse icons:** https://fonts.google.com/icons

The system displays categories as:
```html
<span class="material-symbols-outlined">shopping_cart</span> Groceries
```

### Groups

Create groups for shared expenses:
1. Go to "Groups" → "New Group"
2. Enter group name and description
3. Add members by username (comma-separated)
4. When adding expenses, select the group

## Project Structure

```
expense_tracker/
├── config/                 # Django project settings
│   ├── settings.py        # Main settings (SQLite, media, static)
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py
├── expenses/              # Main app
│   ├── models.py         # Category, Group, Expense models
│   ├── views.py          # All view logic
│   ├── forms.py          # Django forms
│   ├── utils.py          # Gemini AI integration
│   ├── admin.py          # Admin configuration
│   └── urls.py           # App URL patterns
├── templates/             # HTML templates
│   ├── base.html         # Base template with Bootstrap & Material Icons
│   └── expenses/
│       ├── dashboard.html
│       ├── chat_expense.html
│       ├── expense_list.html
│       ├── category_list.html
│       └── group_*.html
├── media/                 # User uploads (receipts)
├── static/               # Static files
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Key Features Explained

### Icon System

Categories use **Google Material Symbol names** stored as text:
- Database field: `icon_name = CharField` (e.g., "shopping_cart")
- HTML rendering: `<span class="material-symbols-outlined">{{ category.icon_name }}</span>`
- AI suggests icons for new categories automatically

### AI Prompt Engineering

The `utils.py` file contains the Gemini prompt that:
1. Receives user input + existing categories/groups
2. Returns structured JSON with parsed expenses
3. Includes `is_new_category` flag
4. Provides `suggested_icon` for new categories

### HTMX Integration

The chat interface uses HTMX for seamless interactions:
- Form submissions update chat without page reload
- Smooth message animations
- Real-time typing indicators

## Database Models

### Category
- `name`: Category name (unique per user)
- `icon_name`: Material Symbol name
- `user`: ForeignKey to User

### Group
- `name`: Group name
- `members`: ManyToMany to User
- `created_by`: ForeignKey to User

### Expense
- `description`: String
- `amount`: Decimal
- `date`: Date
- `category`: ForeignKey to Category (nullable)
- `group`: ForeignKey to Group (nullable)
- `paid_by`: ForeignKey to User
- `receipt_image`: ImageField
- `is_ai_generated`: Boolean flag

## API Integration

### Google Gemini API

The application uses Gemini 1.5 Flash for:
- Natural language understanding
- Expense parsing and extraction
- Category suggestion
- Icon name generation

**Configuration:** Set `GEMINI_API_KEY` in `.env`

## Development

### Adding New Categories Manually

1. Navigate to "Categories"
2. Click "New Category"
3. Enter name and icon
4. Use live preview to verify icon

### Creating Test Data

Use the Django admin panel or Django shell:

```python
python manage.py shell

from django.contrib.auth.models import User
from expenses.models import Category

user = User.objects.first()
Category.objects.create(
    name="Groceries",
    icon_name="shopping_cart",
    user=user
)
```

## Troubleshooting

### AI Chat Not Working
- Verify `GEMINI_API_KEY` is set in `.env`
- Check API quota at Google AI Studio
- View server logs for error messages

### Icons Not Displaying
- Ensure Material Symbols CDN is loaded (check base.html)
- Verify icon name is valid at fonts.google.com/icons
- Check browser console for errors

### Media Files Not Showing
- Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured
- Check that `DEBUG=True` for development
- Verify file permissions on media folder

## Production Deployment

For production:
1. Set `DEBUG=False` in `.env`
2. Configure proper `SECRET_KEY`
3. Set `ALLOWED_HOSTS`
4. Use PostgreSQL instead of SQLite
5. Configure static file serving (WhiteNoise, nginx)
6. Set up media file storage (AWS S3, etc.)
7. Use environment variables for all secrets

## License

This project is for educational purposes.

## Credits

- Django Framework
- Google Gemini AI
- Bootstrap 5
- Google Material Symbols
- HTMX

---

**Built with ❤️ using Django & AI**
