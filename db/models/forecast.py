from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from models.transaction import Transaction
from models.balance_calc import BalanceCalculator
import calendar


@dataclass
class ForecastPoint:
    """A single point in the forecast."""
    date: date
    balance: float
    change: float
    transactions: List[Transaction]
    
    def is_critical(self, threshold: float = 0) -> bool:
        """Check if balance is below critical threshold."""
        return self.balance < threshold
    
    def is_warning(self, threshold: float = 500) -> bool:
        """Check if balance is in warning range."""
        return self.balance < threshold and self.balance >= 0


@dataclass
class MonthForecast:
    """Forecast data for a single month."""
    year: int
    month: int
    month_name: str
    starting_balance: float
    ending_balance: float
    lowest_balance: float
    lowest_balance_date: date
    highest_balance: float
    highest_balance_date: date
    total_income: float
    total_charges: float
    net_change: float
    daily_forecasts: Dict[int, ForecastPoint]
    has_warnings: bool
    has_critical: bool


class ForecastEngine:
    """Advanced forecasting engine for financial planning."""
    
    def __init__(self, starting_balance: float, transactions: List[Transaction]):
        self.starting_balance = starting_balance
        self.transactions = transactions
        self.calculator = BalanceCalculator()
    
    def forecast_months(self, months_ahead: int = 6, 
                       critical_threshold: float = 0,
                       warning_threshold: float = 500) -> List[MonthForecast]:
        """Generate forecast for X months ahead."""
        forecasts = []
        current_balance = self.starting_balance
        today = date.today()
        
        for month_offset in range(months_ahead):
            target_month = today.month + month_offset
            target_year = today.year + (target_month - 1) // 12
            target_month = (target_month - 1) % 12 + 1
            
            month_data = self.calculator.calculate_month_balances(
                current_balance,
                self.transactions,
                target_year,
                target_month
            )
            
            daily_forecasts = {}
            for day, data in month_data.items():
                daily_forecasts[day] = ForecastPoint(
                    date=data['date'],
                    balance=data['balance'],
                    change=data['change'],
                    transactions=data['transactions']
                )
            
            balances = [fp.balance for fp in daily_forecasts.values()]
            
            lowest_balance = min(balances)
            lowest_date = min(daily_forecasts.items(), 
                            key=lambda x: x[1].balance)[1].date
            
            highest_balance = max(balances)
            highest_date = max(daily_forecasts.items(), 
                             key=lambda x: x[1].balance)[1].date
            
            total_income = sum(fp.change for fp in daily_forecasts.values() 
                             if fp.change > 0)
            total_charges = sum(-fp.change for fp in daily_forecasts.values() 
                              if fp.change < 0)
            
            has_warnings = any(fp.is_warning(warning_threshold) 
                              for fp in daily_forecasts.values())
            has_critical = any(fp.is_critical(critical_threshold) 
                              for fp in daily_forecasts.values())
            
            month_forecast = MonthForecast(
                year=target_year,
                month=target_month,
                month_name=calendar.month_name[target_month],
                starting_balance=current_balance,
                ending_balance=list(month_data.values())[-1]['balance'],
                lowest_balance=lowest_balance,
                lowest_balance_date=lowest_date,
                highest_balance=highest_balance,
                highest_balance_date=highest_date,
                total_income=total_income,
                total_charges=total_charges,
                net_change=total_income - total_charges,
                daily_forecasts=daily_forecasts,
                has_warnings=has_warnings,
                has_critical=has_critical
            )
            
            forecasts.append(month_forecast)
            current_balance = month_forecast.ending_balance
        
        return forecasts
    
    def can_afford_purchase(self, amount: float, purchase_date: date, 
                           deadline_date: date,
                           critical_threshold: float = 0) -> Dict:
        """Check if user can afford a purchase and still stay above threshold until deadline."""
        purchase_trans = Transaction(
            id=-1,
            name="Hypothetical Purchase",
            amount=amount,
            type="charge",
            recurrence="once",
            start_date=purchase_date.isoformat(),
            end_date=None,
            day_of_month=None,
            day_of_week=None,
            color="#FF6B6B",
            notes="Scenario planning"
        )
        
        test_transactions = self.transactions + [purchase_trans]
        
        purchase_month_data = self.calculator.calculate_month_balances(
            self.starting_balance,
            test_transactions,
            purchase_date.year,
            purchase_date.month
        )
        
        balance_after_purchase = purchase_month_data[purchase_date.day]['balance']
        
        if deadline_date.month == purchase_date.month and deadline_date.year == purchase_date.year:
            balance_at_deadline = purchase_month_data[deadline_date.day]['balance']
            lowest_after = min(
                purchase_month_data[d]['balance'] 
                for d in range(purchase_date.day, deadline_date.day + 1)
            )
        else:
            deadline_month_data = self.calculator.calculate_month_balances(
                balance_after_purchase,
                test_transactions,
                deadline_date.year,
                deadline_date.month
            )
            balance_at_deadline = deadline_month_data[deadline_date.day]['balance']
            lowest_after = min(balance_after_purchase, 
                              min(deadline_month_data[d]['balance'] 
                                  for d in range(1, deadline_date.day + 1)))
        
        can_afford = (balance_after_purchase >= -amount and 
                     lowest_after >= critical_threshold and
                     balance_at_deadline >= 0)
        
        if not can_afford:
            if lowest_after < critical_threshold:
                message = f"❌ CANNOT AFFORD: Balance would drop to ${lowest_after:,.2f} (below ${critical_threshold:,.2f} threshold)"
            elif balance_at_deadline < 0:
                message = f"❌ CANNOT AFFORD: You'd be broke (${balance_at_deadline:,.2f}) by the deadline"
            else:
                message = "❌ CANNOT AFFORD: Insufficient funds"
        else:
            message = f"✅ CAN AFFORD: After purchase: ${balance_after_purchase:,.2f}. At deadline: ${balance_at_deadline:,.2f}"
        
        return {
            'can_afford': can_afford,
            'balance_after_purchase': balance_after_purchase,
            'lowest_balance_after': lowest_after,
            'balance_at_deadline': balance_at_deadline,
            'will_survive_deadline': balance_at_deadline >= critical_threshold,
            'message': message,
            'recommendation': self._get_recommendation(amount, balance_after_purchase, 
                                                       balance_at_deadline, critical_threshold)
        }
    
    def _get_recommendation(self, purchase_amount: float, balance_after: float,
                           balance_at_deadline: float, threshold: float) -> str:
        """Generate a user-friendly recommendation."""
        if balance_after < 0:
            return "This purchase would put you in overdraft. Consider waiting."
        elif balance_at_deadline < threshold:
            return f"You can make this purchase, but balance at deadline will be low. Consider waiting for more income."
        elif balance_after < purchase_amount * 2:
            return "You can afford this, but your buffer is tight. Be cautious about other expenses."
        else:
            return "You can comfortably afford this purchase."
    
    def find_safe_purchase_date(self, amount: float, deadline_date: date,
                               critical_threshold: float = 0) -> Optional[date]:
        """Find the latest date before deadline when a purchase can be made."""
        current_date = deadline_date - timedelta(days=1)
        
        while current_date >= date.today():
            result = self.can_afford_purchase(
                amount, current_date, deadline_date, critical_threshold
            )
            
            if result['can_afford']:
                return current_date
            
            current_date -= timedelta(days=1)
        
        return None
    
    def get_monthly_summary(self, months_ahead: int = 6) -> List[Dict]:
        """Get a simple summary of each month's finances."""
        forecasts = self.forecast_months(months_ahead)
        summaries = []
        
        for forecast in forecasts:
            summaries.append({
                'month': f"{forecast.month_name} {forecast.year}",
                'starting': forecast.starting_balance,
                'ending': forecast.ending_balance,
                'lowest': forecast.lowest_balance,
                'lowest_date': forecast.lowest_balance_date,
                'income': forecast.total_income,
                'charges': forecast.total_charges,
                'net': forecast.net_change,
                'warning': '⚠️' if forecast.has_warnings else '',
                'critical': '🔴' if forecast.has_critical else ''
            })
        
        return summaries
