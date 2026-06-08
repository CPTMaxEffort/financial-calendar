from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    id: int
    name: str
    amount: float
    type: str  # 'income' or 'charge'
    recurrence: str
    start_date: str
    day_of_month: Optional[int] = None
    day_of_week: Optional[int] = None
    end_date: Optional[str] = None
    color: str = '#FF0000'
    notes: str = ''
    created_at: str = ''
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create Transaction from database row dict."""
        return cls(
            id=data['id'],
            name=data['name'],
            amount=data['amount'],
            type=data['type'],
            recurrence=data['recurrence'],
            start_date=data['start_date'],
            day_of_month=data['day_of_month'],
            day_of_week=data['day_of_week'],
            end_date=data['end_date'],
            color=data['color'],
            notes=data['notes'],
            created_at=data['created_at']
        )
