# Quick Start Guide - Django Expense Tracker

## ✅ Current Status

Your Django Expense Tracker is **fully installed and ready to use**!

- ✅ Django project created
- ✅ Python packages installed
- ✅ Database migrations applied
- ✅ All templates created
- ✅ AI integration configured

## 🚀 Next Steps

### 1. Set Up Your Gemini API Key

Get a free API key from Google:
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

Then create a `.env` file in the project root:

```bash
copy .env.example .env
```

Edit `.env` and add your API key:
```
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True
```

### 2. Create a Superuser Account

```bash
C:/Users/Kavin/Documents/expense_tracker/.venv/Scripts/python.exe manage.py createsuperuser
```

Enter:
- Username (e.g., admin)
- Email (optional)
- Password (twice)

### 3. Run the Development Server

```bash
C:/Users/Kavin/Documents/expense_tracker/.venv/Scripts/python.exe manage.py runserver
```

### 4. Access the Application

Open your browser to:
- **Main App:** http://127.0.0.1:8000
- **Admin Panel:** http://127.0.0.1:8000/admin

## 📱 Using the Application

### AI Chat-Based Entry
1. Click "AI Chat" in the navigation
2. Type expenses naturally, e.g.:
   - "I spent $50 on groceries and $30 on gas"
   - "Bought lunch for $25"
   - "Spent 500 on tent for camping trip group"

### Manual Entry
1. Click "Add Expense" → "Manual Entry"
2. Fill out the form
3. Optionally upload a receipt image

### Creating Categories
1. Navigate to "Categories"
2. Click "New Category"
3. Enter name and Material Icon name
4. Examples: `shopping_cart`, `restaurant`, `local_gas_station`
5. Browse icons: https://fonts.google.com/icons

### Creating Groups
1. Navigate to "Groups"
2. Click "New Group"
3. Enter group name
4. Add members by username (comma-separated)

## 🎨 Material Icons

The app uses Google Material Symbols. Common icons:

- **Shopping:** shopping_cart, shopping_bag, local_mall
- **Food:** restaurant, fastfood, local_cafe, lunch_dining
- **Transport:** local_gas_station, directions_car, flight, train
- **Home:** home, electric_bolt, water_drop, wifi
- **Entertainment:** movie, music_note, sports_tennis, fitness_center
- **Medical:** medical_services, local_pharmacy, health_and_safety
- **Other:** book, school, work, pets, celebration

Full list: https://fonts.google.com/icons

## 🔧 Troubleshooting

### AI Chat Returns Errors
- Make sure `GEMINI_API_KEY` is set in `.env`
- Restart the server after adding the key
- Check API quota at Google AI Studio

### Can't Login
- Make sure you created a superuser (step 2 above)
- Try resetting password: `python manage.py changepassword username`

### Static Files Warning
- This is normal in development
- The warning won't affect functionality

## 📁 Project Structure

```
expense_tracker/
├── config/                # Django settings
├── expenses/              # Main app
│   ├── models.py         # Database models
│   ├── views.py          # View logic
│   ├── forms.py          # Django forms
│   ├── utils.py          # AI integration
│   └── templates/        # HTML templates
├── templates/            # Global templates
├── static/              # CSS/JS files
├── media/               # Uploaded receipts
├── .env                 # Your config (create this!)
├── .env.example         # Example config
├── db.sqlite3           # SQLite database
├── manage.py            # Django management
└── README.md            # Full documentation
```

## 🎯 Features

1. **AI-Powered Entry:** Natural language expense input
2. **Smart Categorization:** Auto-categorize with icon suggestions
3. **Group Expenses:** Track shared expenses
4. **Receipt Upload:** Attach receipt images
5. **Dashboard:** Visual expense overview
6. **Filtering:** Search by category, group, date range
7. **Material Design:** Modern, responsive UI

## 💡 Example Workflows

### Scenario 1: Solo User
1. Login → Create categories (Groceries, Gas, etc.)
2. Use AI Chat: "Spent $100 on groceries and $50 on gas"
3. View dashboard for expense breakdown

### Scenario 2: Group Trip
1. Create group: "Weekend Trip" with friends' usernames
2. Use AI Chat: "Spent $200 on hotel for weekend trip group"
3. View group detail page for member breakdowns

### Scenario 3: Manual Entry with Receipt
1. Click "Add Expense" → Manual Entry
2. Fill form and upload receipt image
3. Receipt appears as thumbnail in expense list

## 🆘 Need Help?

Check the full README.md for:
- Detailed feature explanations
- API integration details
- Production deployment guide
- Development tips

## 🎉 You're All Set!

Your expense tracker is ready to use. Start by:
1. Creating your .env file with API key
2. Creating a superuser
3. Running the server
4. Trying the AI chat with a simple expense!

Happy tracking! 💰
