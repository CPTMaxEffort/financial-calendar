# Financial Calendar Dashboard

A desktop application built with PyQt5 and SQLite that helps you visualize your finances with a calendar view and forecast whether you can afford unexpected purchases without going broke before important dates (like rent day).

## Features

### 📅 Calendar View
- **Month Calendar Display**: See your entire month at a glance with daily balances
- **Color-Coded Days**: Green for positive balance days, red for negative
- **Transaction Details**: Click any day to see all transactions for that day
- **Balance Tracking**: View running balance throughout the month

### 🔮 Financial Forecasting
- **6-Month Outlook**: Project your balance for the next 6 months
- **Low Balance Warnings**: Get alerted when balance drops below thresholds
- **Detailed Day-by-Day**: View day-by-day balance changes with transaction details

### 🎯 Can I Afford This? (Scenario Planning) - **MAIN FEATURE**
Test if you can make a large purchase without going broke before a deadline:

1. **Enter Purchase Amount**: How much do you want to spend?
2. **Select Purchase Date**: When would you buy it?
3. **Set Deadline**: When do you need funds available? (e.g., rent due)
4. **Set Minimum Balance**: What's your safety net? (default: $500)
5. **Get Instant Feedback**: Can you afford it? What's your balance at the deadline?

**Bonus**: Find the best date to make your purchase while staying above your minimum threshold!

### 💰 Recurring Transaction Management
- Add recurring income (paychecks, side gigs)
- Add recurring charges (rent, subscriptions, insurance)
- Support for: Once, Daily, Weekly, Biweekly, Monthly, Annually
- Color-code transactions for easy identification
- Add notes to track purposes

## Installation

### Requirements
- Python 3.7+
- PyQt5

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/CPTMaxEffort/financial-calendar.git
cd financial-calendar
```

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
python main.py
```

## Usage

### Getting Started

1. **Set Your Starting Balance**: Enter your current account balance in the left panel
2. **Add Transactions**: Use the form to add your recurring charges and income:
   - Example: Salary $3000 monthly on the 1st
   - Example: Rent -$1500 monthly on the 1st
   - Example: Subscriptions -$15 monthly on specific days
3. **View Your Calendar**: The calendar shows your projected balance for each day

### Using the Forecast Tab

#### Monthly Summary
- View 6-month outlook with warnings
- See lowest balance for each month
- Identify warning periods ⚠️ and critical periods 🔴

#### Can I Afford? (Main Feature)

Example scenario:
- You want to buy a gaming console for $500
- You could buy it on June 15th
- But rent is due June 1st
- The app will tell you: **YES, you can afford it!** Or **NO, you'd be broke before rent**

Steps:
1. Enter purchase amount ($500)
2. Select when you'd buy it (June 15)
3. Select your deadline (June 1st for rent)
4. Set minimum threshold ($500 safety net)
5. Click "Can I Afford This?"
6. Get results showing if you can afford it and recommendations

**Bonus feature**: Click "Find Best Date to Make Purchase" to get the latest date you can buy while staying safe!

#### Detailed Forecast
- See day-by-day balance changes
- View all transactions for each day
- Identify your cash flow gaps
- Select any month from the dropdown

## Project Structure

```
financial-calendar/
├── main.py                          # Entry point
├── config.py                        # Configuration
├── requirements.txt                 # Dependencies
├── README.md                        # This file
├── db/
│   └── database.py                 # SQLite database management
├── models/
│   ├── transaction.py              # Transaction data model
│   ├── balance_calc.py             # Balance calculation logic
│   └── forecast.py                 # Forecasting engine
└── ui/
    ├── main_window.py              # Main application window
    ├── styles.py                   # Centralized styling
    └── widgets/
        ├── calendar_widget.py      # Calendar display
        ├── transaction_form.py     # Form for adding transactions
        └── forecast_widget.py      # Forecasting UI
```

## How It Works

### Balance Calculation
1. Start with your initial balance
2. For each day in the month:
   - Find all matching recurring transactions
   - Apply charges (negative) and income (positive)
   - Update running balance
3. Display results

### Forecasting Engine
1. Takes your current balance and all recurring transactions
2. Projects forward 6 months
3. Calculates:
   - Daily balances
   - Monthly totals (income, charges, net)
   - Lowest/highest balance points
   - Warning thresholds

### Scenario Planning ("Can I Afford?")
1. Create a hypothetical one-time transaction
2. Add it to your recurring transactions
3. Calculate forward to deadline
4. Check if minimum threshold is maintained
5. Return recommendation

## Color Coding

- 🟢 **Green**: Healthy balance (above $500 or your threshold)
- 🟡 **Yellow**: Warning zone ($0-$500)
- 🔴 **Red**: Critical (below $0)

## Tips

1. **Be Realistic**: Include all recurring expenses, even small subscriptions
2. **Set a Buffer**: Keep a minimum balance above $0 for unexpected costs
3. **Test Scenarios**: Try different purchase amounts/dates before committing
4. **Monitor Warnings**: Pay attention to ⚠️ warning periods
5. **Plan Ahead**: Use the 6-month forecast to identify cash flow patterns

## Database

All data is stored in `financial_calendar.db` (SQLite). The database includes:
- **transactions table**: All your recurring and one-time transactions
- **account_settings table**: Your starting balance and other preferences

The database is created automatically on first run.

## Troubleshooting

### Application won't start
- Make sure you've installed PyQt5: `pip install -r requirements.txt`
- Check Python version is 3.7+: `python --version`

### Database issues
- Delete `financial_calendar.db` to reset (you'll lose all data!)
- It will be recreated on next run

### Forecasting seems wrong
- Make sure all recurring transactions are correctly configured
- Verify your starting balance is accurate
- Check recurrence patterns (monthly vs biweekly)

## Future Features

- [ ] Data export (CSV, JSON)
- [ ] Data import from bank statements
- [ ] Dark mode
- [ ] Multiple accounts
- [ ] Budget tracking
- [ ] Savings goals
- [ ] Charts and visualizations
- [ ] Desktop notifications

## Contributing

Feel free to fork, modify, and improve! This is an open-source project.

## License

MIT License - Feel free to use this for personal or commercial projects.

## Contact

Created by CPTMaxEffort

---

**Start planning your finances today!** 💡
