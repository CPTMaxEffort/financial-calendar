from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QDateEdit, QComboBox,
    QTextEdit, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QBrush
from datetime import date, datetime
import calendar

from models.forecast import ForecastEngine
from models.transaction import Transaction
from db.database import DatabaseManager


class ForecastWidget(QWidget):
    """Widget for displaying financial forecasts and scenario planning."""
    
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.forecast_engine = None
        self.current_forecasts = []
        self.setup_ui()
        self.refresh_forecast()
    
    def setup_ui(self):
        """Initialize the forecast UI."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Financial Forecast")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title)
        
        # Tab widget for different views
        tabs = QTabWidget()
        
        # Tab 1: Monthly Summary
        tabs.addTab(self.create_summary_tab(), "Monthly Summary")
        
        # Tab 2: Scenario Planning
        tabs.addTab(self.create_scenario_tab(), "Can I Afford?")
        
        # Tab 3: Detailed Forecast
        tabs.addTab(self.create_detailed_tab(), "Detailed Forecast")
        
        main_layout.addWidget(tabs)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Forecast")
        refresh_btn.clicked.connect(self.refresh_forecast)
        main_layout.addWidget(refresh_btn)
        
        self.setLayout(main_layout)
    
    def create_summary_tab(self) -> QWidget:
        """Create the monthly summary tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary table
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(10)
        self.summary_table.setHorizontalHeaderLabels([
            "Month", "Starting", "Ending", "Lowest", "Low Date",
            "Income", "Charges", "Net", "Status", "Alert"
        ])
        self.summary_table.horizontalHeader().setStretchLastSection(False)
        self.summary_table.setMinimumHeight(300)
        
        layout.addWidget(QLabel("Next 6 Months Overview:"))
        layout.addWidget(self.summary_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_scenario_tab(self) -> QWidget:
        """Create the scenario planning / 'Can I Afford?' tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        layout.addWidget(QLabel("Can I Afford This Purchase?"))
        
        # Input section
        input_frame = QFrame()
        input_frame.setStyleSheet(
            "QFrame { background-color: #F5F5F5; border-radius: 4px; }"
        )
        input_layout = QVBoxLayout()
        input_layout.setSpacing(8)
        
        # Purchase amount
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Purchase Amount:"))
        self.purchase_amount = QDoubleSpinBox()
        self.purchase_amount.setMinimum(0)
        self.purchase_amount.setMaximum(999999.99)
        self.purchase_amount.setValue(500)
        self.purchase_amount.setSuffix(" USD")
        amount_layout.addWidget(self.purchase_amount)
        amount_layout.addStretch()
        input_layout.addLayout(amount_layout)
        
        # Purchase date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("When would you buy it?"))
        self.purchase_date = QDateEdit()
        self.purchase_date.setDate(QDate.currentDate())
        self.purchase_date.setCalendarPopup(True)
        date_layout.addWidget(self.purchase_date)
        date_layout.addStretch()
        input_layout.addLayout(date_layout)
        
        # Deadline (e.g., rent due)
        deadline_layout = QHBoxLayout()
        deadline_layout.addWidget(QLabel("By when do you need funds? (e.g., rent due):"))
        self.deadline_date = QDateEdit()
        self.deadline_date.setDate(QDate.currentDate().addMonths(1))
        self.deadline_date.setCalendarPopup(True)
        deadline_layout.addWidget(self.deadline_date)
        deadline_layout.addStretch()
        input_layout.addLayout(deadline_layout)
        
        # Minimum balance threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Minimum balance to maintain:"))
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setMinimum(0)
        self.threshold_spin.setMaximum(99999.99)
        self.threshold_spin.setValue(500)
        self.threshold_spin.setSuffix(" USD")
        threshold_layout.addWidget(self.threshold_spin)
        threshold_layout.addStretch()
        input_layout.addLayout(threshold_layout)
        
        input_frame.setLayout(input_layout)
        layout.addWidget(input_frame)
        
        # Check button
        check_btn = QPushButton("Can I Afford This?")
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        check_btn.clicked.connect(self.run_affordability_check)
        layout.addWidget(check_btn)
        
        # Results section
        layout.addWidget(QLabel("Result:"))
        self.affordability_result = QTextEdit()
        self.affordability_result.setReadOnly(True)
        self.affordability_result.setMinimumHeight(200)
        self.affordability_result.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #DDD;
                border-radius: 4px;
                padding: 10px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.affordability_result)
        
        # Find best date button
        find_date_btn = QPushButton("Find Best Date to Make Purchase")
        find_date_btn.clicked.connect(self.find_best_purchase_date)
        layout.addWidget(find_date_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_detailed_tab(self) -> QWidget:
        """Create detailed day-by-day forecast tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Month selector
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Select Month:"))
        self.forecast_month_combo = QComboBox()
        month_layout.addWidget(self.forecast_month_combo)
        month_layout.addStretch()
        layout.addLayout(month_layout)
        
        # Detailed table
        self.detailed_table = QTableWidget()
        self.detailed_table.setColumnCount(6)
        self.detailed_table.setHorizontalHeaderLabels([
            "Day", "Date", "Balance", "Change", "Transactions", "Status"
        ])
        self.detailed_table.setMinimumHeight(400)
        layout.addWidget(self.detailed_table)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_forecast(self):
        """Refresh forecast data from database."""
        try:
            transactions_data = self.db.get_all_transactions()
            transactions = [Transaction.from_dict(t) for t in transactions_data]
            starting_balance = self.db.get_starting_balance()
            
            self.forecast_engine = ForecastEngine(starting_balance, transactions)
            self.current_forecasts = self.forecast_engine.forecast_months(6)
            
            # Update all tabs
            self.update_summary_tab()
            self.update_detailed_tab()
            
        except Exception as e:
            print(f"Error refreshing forecast: {e}")
    
    def update_summary_tab(self):
        """Update the monthly summary table."""
        self.summary_table.setRowCount(0)
        
        summaries = self.forecast_engine.get_monthly_summary(6)
        
        for i, summary in enumerate(summaries):
            self.summary_table.insertRow(i)
            
            # Month
            self.summary_table.setItem(i, 0, QTableWidgetItem(summary['month']))
            
            # Starting balance
            item = QTableWidgetItem(f"${summary['starting']:,.0f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.summary_table.setItem(i, 1, item)
            
            # Ending balance
            item = QTableWidgetItem(f"${summary['ending']:,.0f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if summary['ending'] < 0:
                item.setBackground(QBrush(QColor("#FFCDD2")))
            elif summary['ending'] < 500:
                item.setBackground(QBrush(QColor("#FFF9C4")))
            else:
                item.setBackground(QBrush(QColor("#C8E6C9")))
            self.summary_table.setItem(i, 2, item)
            
            # Lowest balance
            lowest_item = QTableWidgetItem(f"${summary['lowest']:,.0f}")
            lowest_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if summary['lowest'] < 0:
                lowest_item.setBackground(QBrush(QColor("#FFCDD2")))
            elif summary['lowest'] < 500:
                lowest_item.setBackground(QBrush(QColor("#FFF9C4")))
            self.summary_table.setItem(i, 3, lowest_item)
            
            # Lowest date
            self.summary_table.setItem(
                i, 4,
                QTableWidgetItem(summary['lowest_date'].strftime("%b %d"))
            )
            
            # Income
            item = QTableWidgetItem(f"${summary['income']:,.0f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setForeground(QColor("#4CAF50"))
            self.summary_table.setItem(i, 5, item)
            
            # Charges
            item = QTableWidgetItem(f"${summary['charges']:,.0f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setForeground(QColor("#F44336"))
            self.summary_table.setItem(i, 6, item)
            
            # Net
            net_item = QTableWidgetItem(f"${summary['net']:,.0f}")
            net_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.summary_table.setItem(i, 7, net_item)
            
            # Status
            status = ""
            if summary['critical']:
                status += summary['critical'] + " Critical"
            elif summary['warning']:
                status += summary['warning'] + " Warning"
            self.summary_table.setItem(i, 8, QTableWidgetItem(status))
            
            # Alert
            alert = ""
            if summary['critical']:
                alert = "CRITICAL"
            elif summary['warning']:
                alert = "LOW"
            self.summary_table.setItem(i, 9, QTableWidgetItem(alert))
        
        self.summary_table.resizeColumnsToContents()
    
    def update_detailed_tab(self):
        """Update the detailed forecast tab."""
        self.forecast_month_combo.blockSignals(True)
        self.forecast_month_combo.clear()
        
        for forecast in self.current_forecasts:
            display_text = f"{forecast.month_name} {forecast.year}"
            self.forecast_month_combo.addItem(display_text)
        
        self.forecast_month_combo.blockSignals(False)
        self.forecast_month_combo.currentIndexChanged.connect(
            self.on_detailed_month_changed
        )
        
        if self.current_forecasts:
            self.display_detailed_month(0)
    
    def on_detailed_month_changed(self, index: int):
        """Handle month selection in detailed view."""
        if 0 <= index < len(self.current_forecasts):
            self.display_detailed_month(index)
    
    def display_detailed_month(self, forecast_index: int):
        """Display detailed day-by-day forecast for a month."""
        if not (0 <= forecast_index < len(self.current_forecasts)):
            return
        
        forecast = self.current_forecasts[forecast_index]
        self.detailed_table.setRowCount(0)
        
        for day in range(1, len(forecast.daily_forecasts) + 1):
            if day not in forecast.daily_forecasts:
                continue
            
            forecast_point = forecast.daily_forecasts[day]
            row = self.detailed_table.rowCount()
            self.detailed_table.insertRow(row)
            
            # Day
            self.detailed_table.setItem(row, 0, QTableWidgetItem(str(day)))
            
            # Date
            date_item = QTableWidgetItem(
                forecast_point.date.strftime("%a, %b %d")
            )
            self.detailed_table.setItem(row, 1, date_item)
            
            # Balance
            balance_item = QTableWidgetItem(
                f"${forecast_point.balance:,.2f}"
            )
            balance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if forecast_point.balance < 0:
                balance_item.setBackground(QBrush(QColor("#FFCDD2")))
            elif forecast_point.is_warning(500):
                balance_item.setBackground(QBrush(QColor("#FFF9C4")))
            else:
                balance_item.setBackground(QBrush(QColor("#C8E6C9")))
            
            self.detailed_table.setItem(row, 2, balance_item)
            
            # Change
            change_item = QTableWidgetItem(
                f"${forecast_point.change:+,.2f}"
            )
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if forecast_point.change > 0:
                change_item.setForeground(QColor("#4CAF50"))
            elif forecast_point.change < 0:
                change_item.setForeground(QColor("#F44336"))
            self.detailed_table.setItem(row, 3, change_item)
            
            # Transactions
            trans_text = "; ".join(
                f"{t.name} (${t.amount:,.0f})"
                for t in forecast_point.transactions
            )
            self.detailed_table.setItem(
                row, 4, QTableWidgetItem(trans_text if trans_text else "—")
            )
            
            # Status
            status = ""
            if forecast_point.is_critical():
                status = "🔴 CRITICAL"
            elif forecast_point.is_warning():
                status = "⚠️ LOW"
            self.detailed_table.setItem(row, 5, QTableWidgetItem(status))
        
        self.detailed_table.resizeColumnsToContents()
    
    def run_affordability_check(self):
        """Run the affordability check and display results."""
        if not self.forecast_engine:
            self.affordability_result.setText("Error: No forecast data available.")
            return
        
        amount = self.purchase_amount.value()
        purchase_date = self.purchase_date.date().toPyDate()
        deadline_date = self.deadline_date.date().toPyDate()
        threshold = self.threshold_spin.value()
        
        if purchase_date > deadline_date:
            self.affordability_result.setText(
                "❌ Error: Purchase date must be before deadline date."
            )
            return
        
        if purchase_date < date.today():
            self.affordability_result.setText(
                "❌ Error: Purchase date cannot be in the past."
            )
            return
        
        result = self.forecast_engine.can_afford_purchase(
            amount, purchase_date, deadline_date, threshold
        )
        
        output = f"""
══════════════════════════════════════════════════════════════════
                    AFFORDABILITY CHECK
══════════════════════════════════════════════════════════════════

PURCHASE DETAILS:
  Amount: ${amount:,.2f}
  Purchase Date: {purchase_date.strftime('%A, %B %d, %Y')}
  Deadline: {deadline_date.strftime('%A, %B %d, %Y')}
  Minimum Balance Threshold: ${threshold:,.2f}

RESULTS:
{result['message']}

FINANCIAL PROJECTION:
  Balance after purchase: ${result['balance_after_purchase']:,.2f}
  Lowest balance until deadline: ${result['lowest_balance_after']:,.2f}
  Balance at deadline: ${result['balance_at_deadline']:,.2f}
  Will survive until deadline: {'✓ YES' if result['will_survive_deadline'] else '✗ NO'}

RECOMMENDATION:
{result['recommendation']}

══════════════════════════════════════════════════════════════════
        """
        
        self.affordability_result.setText(output)
    
    def find_best_purchase_date(self):
        """Find the best date to make a purchase."""
        if not self.forecast_engine:
            self.affordability_result.setText("Error: No forecast data available.")
            return
        
        amount = self.purchase_amount.value()
        deadline_date = self.deadline_date.date().toPyDate()
        threshold = self.threshold_spin.value()
        
        best_date = self.forecast_engine.find_safe_purchase_date(
            amount, deadline_date, threshold
        )
        
        if best_date:
            output = f"""
══════════════════════════════════════════════════════════════════
             OPTIMAL PURCHASE DATE FINDER
══════════════════════════════════════════════════════════════════

✓ RECOMMENDED: You can make this purchase!

  Best Date: {best_date.strftime('%A, %B %d, %Y')}
  Amount: ${amount:,.2f}
  Deadline: {deadline_date.strftime('%A, %B %d, %Y')}

Wait until {best_date.strftime('%B %d')} to ensure you have
enough buffer before the deadline. This gives you the most
flexibility while staying safely above ${threshold:,.2f}.

══════════════════════════════════════════════════════════════════
            """
        else:
            output = f"""
══════════════════════════════════════════════════════════════════
             OPTIMAL PURCHASE DATE FINDER
══════════════════════════════════════════════════════════════════

✗ NOT RECOMMENDED: Cannot find a safe date

  Amount: ${amount:,.2f}
  Deadline: {deadline_date.strftime('%A, %B %d, %Y')}
  Required Minimum: ${threshold:,.2f}

Based on your current recurring transactions and balance,
there is no date between today and the deadline where you
can make this purchase and maintain the minimum balance.

Options:
  1. Reduce the purchase amount
  2. Delay the purchase (move deadline later)
  3. Increase your income with a new transaction
  4. Reduce recurring charges

══════════════════════════════════════════════════════════════════
            """
        
        self.affordability_result.setText(output)
