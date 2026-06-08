import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import config


class DatabaseManager:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'charge')),
                recurrence TEXT NOT NULL CHECK(recurrence IN 
                    ('once', 'daily', 'weekly', 'biweekly', 'monthly', 'annually')),
                day_of_month INTEGER,
                day_of_week INTEGER,
                start_date TEXT NOT NULL,
                end_date TEXT,
                color TEXT DEFAULT '#FF0000',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                starting_balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM account_settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'INSERT INTO account_settings (id, starting_balance) VALUES (1, 0)'
            )
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, name: str, amount: float, type_: str, 
                       recurrence: str, start_date: str, 
                       day_of_month: Optional[int] = None,
                       day_of_week: Optional[int] = None,
                       end_date: Optional[str] = None,
                       color: str = '#FF0000',
                       notes: str = '') -> int:
        """Add a new transaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions 
            (name, amount, type, recurrence, day_of_month, day_of_week, 
             start_date, end_date, color, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, amount, type_, recurrence, day_of_month, day_of_week,
              start_date, end_date, color, notes))
        
        conn.commit()
        trans_id = cursor.lastrowid
        conn.close()
        return trans_id
    
    def get_all_transactions(self) -> List[dict]:
        """Retrieve all transactions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions ORDER BY created_at DESC')
        transactions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return transactions
    
    def update_transaction(self, trans_id: int, **kwargs):
        """Update a transaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        allowed_fields = {'name', 'amount', 'type', 'recurrence', 'day_of_month',
                         'day_of_week', 'start_date', 'end_date', 'color', 'notes'}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not fields:
            conn.close()
            return
        
        fields['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f'{k} = ?' for k in fields.keys()])
        values = list(fields.values()) + [trans_id]
        
        cursor.execute(f'UPDATE transactions SET {set_clause} WHERE id = ?', values)
        conn.commit()
        conn.close()
    
    def delete_transaction(self, trans_id: int):
        """Delete a transaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
        conn.commit()
        conn.close()
    
    def get_starting_balance(self) -> float:
        """Get the current starting balance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT starting_balance FROM account_settings WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0
    
    def set_starting_balance(self, balance: float):
        """Update the starting balance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE account_settings SET starting_balance = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1',
            (balance,)
        )
        conn.commit()
        conn.close()
