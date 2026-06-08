"""Application configuration and constants."""

from enum import Enum
from pathlib import Path

# Database
DATABASE_PATH = "financial_calendar.db"

# UI Configuration
WINDOW_TITLE = "Financial Calendar Dashboard"
DEFAULT_WINDOW_WIDTH = 1600
DEFAULT_WINDOW_HEIGHT = 900

# Currency
CURRENCY_SYMBOL = "$"
CURRENCY_CODE = "USD"
DECIMAL_PLACES = 2

# Forecasting
DEFAULT_FORECAST_MONTHS = 6
DEFAULT_CRITICAL_THRESHOLD = 0  # Below $0 is critical
DEFAULT_WARNING_THRESHOLD = 500  # Below $500 is warning

# Theme
class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"

DEFAULT_THEME = Theme.LIGHT

# Recurrence types
RECURRENCE_TYPES = [
    ("once", "Once"),
    ("daily", "Daily"),
    ("weekly", "Weekly"),
    ("biweekly", "Biweekly"),
    ("monthly", "Monthly"),
    ("annually", "Annually")
]

# Transaction types
TRANSACTION_TYPES = [
    ("income", "Income"),
    ("charge", "Charge")
]
