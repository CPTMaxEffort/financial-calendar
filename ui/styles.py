from enum import Enum
import config


class Colors:
    # Light theme
    LIGHT_BG = "#FFFFFF"
    LIGHT_TEXT = "#000000"
    LIGHT_SECONDARY = "#F5F5F5"
    
    # Dark theme
    DARK_BG = "#1E1E1E"
    DARK_TEXT = "#FFFFFF"
    DARK_SECONDARY = "#2D2D2D"
    
    # Semantic colors
    POSITIVE = "#4CAF50"  # Green
    NEGATIVE = "#F44336"  # Red
    NEUTRAL = "#2196F3"   # Blue
    WARNING = "#FF9800"   # Orange
    
    @staticmethod
    def get_bg_color(theme: config.Theme) -> str:
        return Colors.LIGHT_BG if theme == config.Theme.LIGHT else Colors.DARK_BG
    
    @staticmethod
    def get_text_color(theme: config.Theme) -> str:
        return Colors.LIGHT_TEXT if theme == config.Theme.LIGHT else Colors.DARK_TEXT


class Fonts:
    TITLE = "Arial, 16pt, bold"
    HEADING = "Arial, 12pt, bold"
    NORMAL = "Arial, 10pt"
    SMALL = "Arial, 9pt"


def get_stylesheet(theme: config.Theme = config.Theme.LIGHT) -> str:
    """Generate QSS stylesheet dynamically."""
    bg = Colors.get_bg_color(theme)
    text = Colors.get_text_color(theme)
    secondary = Colors.LIGHT_SECONDARY if theme == config.Theme.LIGHT else Colors.DARK_SECONDARY
    
    return f"""
    QMainWindow {{
        background-color: {bg};
        color: {text};
    }}
    
    QWidget {{
        background-color: {bg};
        color: {text};
    }}
    
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
        background-color: {secondary};
        color: {text};
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 5px;
    }}
    
    QPushButton {{
        background-color: {Colors.NEUTRAL};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    
    QPushButton:hover {{
        background-color: #1976D2;
    }}
    
    QLabel {{
        color: {text};
    }}
    
    QTableWidget {{
        background-color: {secondary};
        color: {text};
        gridline-color: #CCCCCC;
    }}
    
    QHeaderView::section {{
        background-color: {Colors.NEUTRAL};
        color: white;
        padding: 5px;
        border: none;
    }}
    
    QTabWidget::pane {{
        border: 1px solid #CCCCCC;
    }}
    
    QTabBar::tab {{
        background-color: {secondary};
        color: {text};
        padding: 8px 20px;
        border: 1px solid #CCCCCC;
    }}
    
    QTabBar::tab:selected {{
        background-color: {Colors.NEUTRAL};
        color: white;
    }}
    
    QFrame {{
        border: 1px solid #CCCCCC;
        border-radius: 4px;
    }}
    """
