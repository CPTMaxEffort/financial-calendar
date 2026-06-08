from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QFrame, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from datetime import date
import calendar


class DayBox(QFrame):
    """Custom widget for each calendar day."""
    clicked = pyqtSignal(int)  # day number
    
    def __init__(self, day: int, balance: float, change: float, color: str = None):
        super().__init__()
        self.day = day
        self.balance = balance
        self.change = change
        self.transaction_color = color
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Day number
        day_label = QLabel(str(self.day))
        day_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(day_label)
        
        # Balance
        balance_label = QLabel(f"${self.balance:,.2f}")
        balance_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(balance_label)
        
        # Change
        change_text = f"{'▲' if self.change >= 0 else '▼'} ${abs(self.change):,.2f}"
        change_label = QLabel(change_text)
        change_label.setFont(QFont("Arial", 9))
        
        # Color code the change
        if self.change > 0:
            change_label.setStyleSheet("color: #4CAF50;")  # Green
        elif self.change < 0:
            change_label.setStyleSheet("color: #F44336;")  # Red
        else:
            change_label.setStyleSheet("color: #999999;")  # Gray
        
        layout.addWidget(change_label)
        self.setLayout(layout)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #F9F9F9;
                border: 1px solid #DDD;
                border-radius: 4px;
            }
            QFrame:hover {
                background-color: #F0F0F0;
            }
        """)
        self.setMinimumHeight(100)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.day)


class CalendarWidget(QWidget):
    """Main calendar display widget."""
    day_selected = pyqtSignal(int, dict)  # day, day_data
    
    def __init__(self):
        super().__init__()
        self.current_year = date.today().year
        self.current_month = date.today().month
        self.month_data = {}
        self.day_boxes = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Month/Year header
        self.header_label = QLabel()
        self.header_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header_label)
        
        # Calendar grid
        self.grid = QGridLayout()
        self.grid.setSpacing(8)
        layout.addLayout(self.grid)
        
        self.setLayout(layout)
        self.update_calendar()
    
    def update_calendar(self, month_data: dict = None):
        """Update calendar display with new month data."""
        if month_data:
            self.month_data = month_data
        
        self.header_label.setText(
            f"{calendar.month_name[self.current_month]} {self.current_year}"
        )
        
        # Clear existing day boxes
        for box in self.day_boxes.values():
            box.deleteLater()
        self.day_boxes.clear()
        
        # Clear grid
        while self.grid.count():
            self.grid.itemAt(0).widget().deleteLater()
        
        # Add weekday headers
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for col, weekday in enumerate(weekdays):
            label = QLabel(weekday)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, 0, col)
        
        # Add day boxes
        first_day = calendar.monthrange(self.current_year, self.current_month)[0]
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        row = 1
        col = first_day
        
        for day in range(1, days_in_month + 1):
            day_info = self.month_data.get(day, {
                'balance': 0,
                'change': 0,
                'transactions': []
            })
            
            day_box = DayBox(
                day,
                day_info['balance'],
                day_info['change']
            )
            day_box.clicked.connect(
                lambda d=day: self.day_selected.emit(d, self.month_data.get(d, {}))
            )
            
            self.grid.addWidget(day_box, row, col)
            self.day_boxes[day] = day_box
            
            col += 1
            if col > 6:  # Sunday = 6
                col = 0
                row += 1
    
    def next_month(self):
        """Navigate to next month."""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()
    
    def previous_month(self):
        """Navigate to previous month."""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()
