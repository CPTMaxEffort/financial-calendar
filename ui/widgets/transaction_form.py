from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QSpinBox, QDateEdit, 
                             QPushButton, QTextEdit, QColorDialog, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QColor, QFont
from datetime import datetime


class TransactionForm(QWidget):
    """Form to add/edit recurring transactions."""
    transaction_added = pyqtSignal(dict)
    transaction_updated = pyqtSignal(int, dict)
    
    def __init__(self):
        super().__init__()
        self.edit_mode = False
        self.edit_id = None
        self.selected_color = '#FF0000'
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Add Transaction")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Rent, Salary")
        layout.addWidget(self.name_input)
        
        # Amount
        layout.addWidget(QLabel("Amount:"))
        amount_layout = QHBoxLayout()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimum(0)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" USD")
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)
        
        # Type
        layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Income", "Charge"])
        layout.addWidget(self.type_combo)
        
        # Recurrence
        layout.addWidget(QLabel("Recurrence:"))
        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems(
            ["Once", "Daily", "Weekly", "Biweekly", "Monthly", "Annually"]
        )
        self.recurrence_combo.currentTextChanged.connect(self.on_recurrence_changed)
        layout.addWidget(self.recurrence_combo)
        
        # Day of month (for monthly)
        layout.addWidget(QLabel("Day of Month:"))
        self.day_of_month_spin = QSpinBox()
        self.day_of_month_spin.setMinimum(1)
        self.day_of_month_spin.setMaximum(31)
        self.day_of_month_spin.setValue(1)
        self.day_of_month_spin.setVisible(False)
        layout.addWidget(self.day_of_month_spin)
        
        # Day of week (for weekly)
        layout.addWidget(QLabel("Day of Week:"))
        self.day_of_week_combo = QComboBox()
        self.day_of_week_combo.addItems(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
        self.day_of_week_combo.setVisible(False)
        layout.addWidget(self.day_of_week_combo)
        
        # Start date
        layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        layout.addWidget(self.start_date)
        
        # End date
        layout.addWidget(QLabel("End Date (optional):"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        layout.addWidget(self.end_date)
        
        # Color picker
        layout.addWidget(QLabel("Color:"))
        color_layout = QHBoxLayout()
        self.color_display = QPushButton()
        self.color_display.setMaximumWidth(50)
        self.color_display.setStyleSheet(f"background-color: {self.selected_color};")
        self.color_display.clicked.connect(self.pick_color)
        color_layout.addWidget(self.color_display)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Notes
        layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("Add Transaction")
        self.submit_btn.clicked.connect(self.submit_form)
        button_layout.addWidget(self.submit_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setVisible(False)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def on_recurrence_changed(self, text):
        """Show/hide relevant fields based on recurrence type."""
        if text == "Monthly":
            self.day_of_month_spin.setVisible(True)
            self.day_of_week_combo.setVisible(False)
        elif text == "Weekly" or text == "Biweekly":
            self.day_of_month_spin.setVisible(False)
            self.day_of_week_combo.setVisible(True)
        else:
            self.day_of_month_spin.setVisible(False)
            self.day_of_week_combo.setVisible(False)
    
    def pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_display.setStyleSheet(f"background-color: {self.selected_color};")
    
    def submit_form(self):
        """Submit the form."""
        data = {
            'name': self.name_input.text(),
            'amount': self.amount_input.value(),
            'type': self.type_combo.currentText().lower(),
            'recurrence': self.recurrence_combo.currentText().lower(),
            'day_of_month': self.day_of_month_spin.value() if self.day_of_month_spin.isVisible() else None,
            'day_of_week': self.day_of_week_combo.currentIndex() if self.day_of_week_combo.isVisible() else None,
            'start_date': self.start_date.date().toPyDate().isoformat(),
            'end_date': self.end_date.date().toPyDate().isoformat() if self.end_date.date() > self.start_date.date() else None,
            'color': self.selected_color,
            'notes': self.notes_input.toPlainText()
        }
        
        if not data['name']:
            return
        
        if self.edit_mode:
            self.transaction_updated.emit(self.edit_id, data)
            self.cancel_edit()
        else:
            self.transaction_added.emit(data)
            self.clear_form()
    
    def clear_form(self):
        """Clear all form fields."""
        self.name_input.clear()
        self.amount_input.setValue(0)
        self.type_combo.setCurrentIndex(0)
        self.recurrence_combo.setCurrentIndex(0)
        self.day_of_month_spin.setValue(1)
        self.day_of_week_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate())
        self.notes_input.clear()
        self.selected_color = '#FF0000'
        self.color_display.setStyleSheet(f"background-color: {self.selected_color};")
    
    def load_transaction(self, trans_id: int, trans_data: dict):
        """Load transaction data for editing."""
        self.edit_mode = True
        self.edit_id = trans_id
        
        self.name_input.setText(trans_data['name'])
        self.amount_input.setValue(trans_data['amount'])
        self.type_combo.setCurrentText(trans_data['type'].capitalize())
        self.recurrence_combo.setCurrentText(trans_data['recurrence'].capitalize())
        
        if trans_data['day_of_month']:
            self.day_of_month_spin.setValue(trans_data['day_of_month'])
        if trans_data['day_of_week'] is not None:
            self.day_of_week_combo.setCurrentIndex(trans_data['day_of_week'])
        
        self.start_date.setDate(QDate.fromisoformat(trans_data['start_date']))
        if trans_data['end_date']:
            self.end_date.setDate(QDate.fromisoformat(trans_data['end_date']))
        
        self.selected_color = trans_data['color']
        self.color_display.setStyleSheet(f"background-color: {self.selected_color};")
        self.notes_input.setPlainText(trans_data['notes'])
        
        self.submit_btn.setText("Update Transaction")
        self.cancel_btn.setVisible(True)
        self.on_recurrence_changed(self.recurrence_combo.currentText())
    
    def cancel_edit(self):
        """Exit edit mode."""
        self.edit_mode = False
        self.edit_id = None
        self.submit_btn.setText("Add Transaction")
        self.cancel_btn.setVisible(False)
        self.clear_form()
