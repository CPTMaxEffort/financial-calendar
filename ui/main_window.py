from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QPushButton, QLabel, QSpinBox, 
    QTableWidget, QTableWidgetItem, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from datetime import date

from db.database import DatabaseManager
from models.transaction import Transaction
from models.balance_calc import BalanceCalculator
from ui.widgets.calendar_widget import CalendarWidget
from ui.widgets.transaction_form import TransactionForm
from ui.widgets.forecast_widget import ForecastWidget
from ui.styles import get_stylesheet
import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.DEFAULT_WINDOW_WIDTH, config.DEFAULT_WINDOW_HEIGHT)
        
        # Initialize database and data
        self.db = DatabaseManager()
        self.calculator = BalanceCalculator()
        self.current_theme = config.DEFAULT_THEME
        
        # Apply stylesheet
        self.setStyleSheet(get_stylesheet(self.current_theme))
        
        # Build UI
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel: Form and settings
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        
        # Starting balance
        balance_layout = QVBoxLayout()
        balance_label = QLabel("Starting Balance:")
        balance_label.setFont(QFont("Arial", 10, QFont.Bold))
        balance_layout.addWidget(balance_label)
        
        balance_input_layout = QHBoxLayout()
        self.balance_spin = QSpinBox()
        self.balance_spin.setMinimum(-999999)
        self.balance_spin.setMaximum(999999)
        self.balance_spin.setValue(int(self.db.get_starting_balance()))
        self.balance_spin.setSuffix(" USD")
        balance_input_layout.addWidget(self.balance_spin)
        
        save_balance_btn = QPushButton("Save")
        save_balance_btn.clicked.connect(self.save_starting_balance)
        balance_input_layout.addWidget(save_balance_btn)
        
        balance_layout.addLayout(balance_input_layout)
        left_layout.addLayout(balance_layout)
        
        # Transaction form
        self.form = TransactionForm()
        self.form.transaction_added.connect(self.on_transaction_added)
        self.form.transaction_updated.connect(self.on_transaction_updated)
        left_layout.addWidget(QLabel("Transactions:"))
        left_layout.addWidget(self.form)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(350)
        
        # Right panel: Calendar and transactions
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        
        # Tab widget for calendar and forecast
        tabs = QTabWidget()
        
        # Calendar tab
        calendar_tab = QWidget()
        calendar_layout = QVBoxLayout()
        
        # Month navigation
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("← Previous")
        prev_btn.clicked.connect(self.on_previous_month)
        nav_layout.addWidget(prev_btn)
        
        nav_layout.addStretch()
        
        next_btn = QPushButton("Next →")
        next_btn.clicked.connect(self.on_next_month)
        nav_layout.addWidget(next_btn)
        
        calendar_layout.addLayout(nav_layout)
        
        # Calendar
        self.calendar_widget = CalendarWidget()
        self.calendar_widget.day_selected.connect(self.on_day_selected)
        calendar_layout.addWidget(self.calendar_widget)
        
        # Day details
        calendar_layout.addWidget(QLabel("Transactions for Selected Day:"))
        self.day_transactions_table = QTableWidget()
        self.day_transactions_table.setColumnCount(4)
        self.day_transactions_table.setHorizontalHeaderLabels(
            ["Name", "Amount", "Type", "Actions"]
        )
        self.day_transactions_table.setMaximumHeight(150)
        calendar_layout.addWidget(self.day_transactions_table)
        
        calendar_tab.setLayout(calendar_layout)
        tabs.addTab(calendar_tab, "Calendar View")
        
        # Forecast tab
        self.forecast_widget = ForecastWidget(self.db)
        tabs.addTab(self.forecast_widget, "Forecast & Planning")
        
        right_layout.addWidget(tabs)
        right_panel.setLayout(right_layout)
        
        # Add splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        central.setLayout(main_layout)
    
    def load_data(self):
        """Load data from database and refresh UI."""
        transactions_data = self.db.get_all_transactions()
        transactions = [Transaction.from_dict(t) for t in transactions_data]
        
        # Calculate month data
        today = date.today()
        month_data = self.calculator.calculate_month_balances(
            self.db.get_starting_balance(),
            transactions,
            today.year,
            today.month
        )
        
        self.calendar_widget.update_calendar(month_data)
        self.forecast_widget.refresh_forecast()
    
    @pyqtSlot(dict)
    def on_transaction_added(self, data):
        """Handle new transaction added."""
        self.db.add_transaction(
            name=data['name'],
            amount=data['amount'],
            type_=data['type'],
            recurrence=data['recurrence'],
            day_of_month=data['day_of_month'],
            day_of_week=data['day_of_week'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            color=data['color'],
            notes=data['notes']
        )
        self.load_data()
    
    @pyqtSlot(int, dict)
    def on_transaction_updated(self, trans_id, data):
        """Handle transaction updated."""
        self.db.update_transaction(trans_id, **data)
        self.load_data()
    
    @pyqtSlot()
    def save_starting_balance(self):
        """Save the starting balance."""
        self.db.set_starting_balance(self.balance_spin.value())
        self.load_data()
    
    @pyqtSlot()
    def on_previous_month(self):
        """Navigate to previous month."""
        self.calendar_widget.previous_month()
        self.load_data()
    
    @pyqtSlot()
    def on_next_month(self):
        """Navigate to next month."""
        self.calendar_widget.next_month()
        self.load_data()
    
    @pyqtSlot(int, dict)
    def on_day_selected(self, day: int, day_data: dict):
        """Handle day selection to show transactions."""
        self.day_transactions_table.setRowCount(0)
        
        for trans in day_data.get('transactions', []):
            row = self.day_transactions_table.rowCount()
            self.day_transactions_table.insertRow(row)
            
            self.day_transactions_table.setItem(row, 0, QTableWidgetItem(trans.name))
            self.day_transactions_table.setItem(row, 1, QTableWidgetItem(f"${trans.amount:,.2f}"))
            self.day_transactions_table.setItem(row, 2, QTableWidgetItem(trans.type))
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, t=trans: self.edit_transaction(t))
            self.day_transactions_table.setCellWidget(row, 3, edit_btn)
    
    def edit_transaction(self, trans: Transaction):
        """Load transaction for editing."""
        trans_dict = {
            'id': trans.id,
            'name': trans.name,
            'amount': trans.amount,
            'type': trans.type,
            'recurrence': trans.recurrence,
            'day_of_month': trans.day_of_month,
            'day_of_week': trans.day_of_week,
            'start_date': trans.start_date,
            'end_date': trans.end_date,
            'color': trans.color,
            'notes': trans.notes
        }
        self.form.load_transaction(trans.id, trans_dict)
