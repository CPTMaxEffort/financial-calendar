from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple
from models.transaction import Transaction


class BalanceCalculator:
    @staticmethod
    def get_transactions_for_day(transactions: List[Transaction], target_date: date) -> List[Transaction]:
        """Get all transactions that apply to a specific day."""
        matching = []
        
        for trans in transactions:
            start = datetime.fromisoformat(trans.start_date).date()
            end = None
            
            if trans.end_date:
                end = datetime.fromisoformat(trans.end_date).date()
            
            # Check if date is in valid range
            if target_date < start or (end and target_date > end):
                continue
            
            # Check recurrence pattern
            if trans.recurrence == 'once':
                if target_date == start:
                    matching.append(trans)
            
            elif trans.recurrence == 'daily':
                matching.append(trans)
            
            elif trans.recurrence == 'weekly':
                if target_date.weekday() == trans.day_of_week:
                    matching.append(trans)
            
            elif trans.recurrence == 'biweekly':
                days_diff = (target_date - start).days
                if days_diff >= 0 and days_diff % 14 == 0 and target_date.weekday() == trans.day_of_week:
                    matching.append(trans)
            
            elif trans.recurrence == 'monthly':
                if target_date.day == trans.day_of_month:
                    matching.append(trans)
            
            elif trans.recurrence == 'annually':
                if target_date.month == start.month and target_date.day == start.day:
                    matching.append(trans)
        
        return matching
    
    @staticmethod
    def calculate_month_balances(
        starting_balance: float,
        transactions: List[Transaction],
        year: int,
        month: int
    ) -> Dict[int, Dict]:
        """
        Calculate balance for each day in a month.
        
        Returns: {day: {'balance': X, 'change': Y, 'transactions': [...], 'date': ...}}
        """
        import calendar
        
        days_in_month = calendar.monthrange(year, month)[1]
        result = {}
        running_balance = starting_balance
        
        for day in range(1, days_in_month + 1):
            target_date = date(year, month, day)
            day_transactions = BalanceCalculator.get_transactions_for_day(transactions, target_date)
            
            # Calculate change for this day
            change = sum(
                trans.amount if trans.type == 'income' else -trans.amount
                for trans in day_transactions
            )
            
            running_balance += change
            
            result[day] = {
                'balance': running_balance,
                'change': change,
                'transactions': day_transactions,
                'date': target_date
            }
        
        return result
