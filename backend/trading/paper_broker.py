"""
Paper Trading Broker
Simulates trade execution with realistic fills
"""
import uuid
from typing import Dict, Optional
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)


class PaperBroker:
    """Simulates order execution for paper trading"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.initial_capital = self.config.get('initial_capital', 100000.0)
        self.cash = self.initial_capital
        self.positions: Dict[str, Dict] = {}
        self.slippage_percent = self.config.get('slippage_percent', 0.1)  # 0.1% slippage
        
    def execute_buy(self, symbol: str, quantity: int, price: float) -> Dict:
        """Execute a buy order"""
        # Apply slippage
        fill_price = price * (1 + random.uniform(0, self.slippage_percent / 100))
        total_cost = fill_price * quantity
        
        if total_cost > self.cash:
            logger.warning(f"Insufficient cash for {symbol}: need {total_cost}, have {self.cash}")
            return {
                'status': 'REJECTED',
                'reason': 'Insufficient cash',
                'symbol': symbol,
                'quantity': quantity
            }
        
        # Update cash and positions
        self.cash -= total_cost
        
        if symbol in self.positions:
            # Average down/up
            current_qty = self.positions[symbol]['quantity']
            current_avg = self.positions[symbol]['avg_price']
            new_avg = ((current_avg * current_qty) + (fill_price * quantity)) / (current_qty + quantity)
            
            self.positions[symbol]['quantity'] += quantity
            self.positions[symbol]['avg_price'] = new_avg
        else:
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_price': fill_price,
                'side': 'LONG'
            }
        
        order_id = f"BUY_{symbol}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Executed BUY: {quantity} {symbol} @ ${fill_price:.2f}")
        
        return {
            'status': 'FILLED',
            'order_id': order_id,
            'symbol': symbol,
            'side': 'BUY',
            'quantity': quantity,
            'fill_price': fill_price,
            'total_cost': total_cost,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def execute_sell(self, symbol: str, quantity: int, price: float) -> Dict:
        """Execute a sell order"""
        if symbol not in self.positions:
            return {
                'status': 'REJECTED',
                'reason': 'No position to sell',
                'symbol': symbol
            }
        
        position = self.positions[symbol]
        if position['quantity'] < quantity:
            return {
                'status': 'REJECTED',
                'reason': f"Insufficient quantity: have {position['quantity']}, need {quantity}",
                'symbol': symbol
            }
        
        # Apply slippage (negative for sells)
        fill_price = price * (1 - random.uniform(0, self.slippage_percent / 100))
        total_proceeds = fill_price * quantity
        
        # Update cash and positions
        self.cash += total_proceeds
        
        # Calculate P&L for this sale
        cost_basis = position['avg_price'] * quantity
        pnl = total_proceeds - cost_basis
        pnl_percent = (pnl / cost_basis) * 100
        
        # Update or remove position
        position['quantity'] -= quantity
        if position['quantity'] == 0:
            del self.positions[symbol]
        
        order_id = f"SELL_{symbol}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Executed SELL: {quantity} {symbol} @ ${fill_price:.2f}, P&L: ${pnl:.2f}")
        
        return {
            'status': 'FILLED',
            'order_id': order_id,
            'symbol': symbol,
            'side': 'SELL',
            'quantity': quantity,
            'fill_price': fill_price,
            'total_proceeds': total_proceeds,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for a symbol"""
        return self.positions.get(symbol)
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        positions_value = sum(
            pos['quantity'] * current_prices.get(symbol, pos['avg_price'])
            for symbol, pos in self.positions.items()
        )
        return self.cash + positions_value
    
    def get_account_summary(self, current_prices: Dict[str, float]) -> Dict:
        """Get account summary"""
        portfolio_value = self.get_portfolio_value(current_prices)
        positions_value = portfolio_value - self.cash
        
        return {
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': portfolio_value,
            'initial_capital': self.initial_capital,
            'total_pnl': portfolio_value - self.initial_capital,
            'total_pnl_percent': ((portfolio_value - self.initial_capital) / self.initial_capital) * 100,
            'positions_count': len(self.positions),
            'buying_power': self.cash
        }
    
    def can_afford(self, quantity: int, price: float) -> bool:
        """Check if can afford a trade"""
        total_cost = quantity * price * 1.01  # Add buffer for slippage
        return total_cost <= self.cash
