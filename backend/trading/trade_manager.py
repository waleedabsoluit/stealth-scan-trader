"""
Trade Manager - Manages trade lifecycle
"""
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from backend.database.models import Trade, Signal
from backend.database.repositories.trade_repository import TradeRepository
from backend.trading.paper_broker import PaperBroker

logger = logging.getLogger(__name__)


class TradeManager:
    """Manages trade execution and lifecycle"""
    
    def __init__(self, db: Session, broker: PaperBroker, config: Dict = None):
        self.db = db
        self.broker = broker
        self.config = config or {}
        self.trade_repo = TradeRepository(db)
        self.default_position_size = self.config.get('default_position_size', 1000.0)
        self.max_position_size = self.config.get('max_position_size', 5000.0)
    
    def execute_signal(self, signal: Signal, current_price: float) -> Optional[Trade]:
        """Execute a trade from a signal"""
        # Calculate position size based on confidence and tier
        position_size = self._calculate_position_size(signal)
        quantity = int(position_size / current_price)
        
        if quantity <= 0:
            logger.warning(f"Calculated quantity is 0 for {signal.symbol}")
            return None
        
        # Check if broker can afford
        if not self.broker.can_afford(quantity, current_price):
            logger.warning(f"Cannot afford trade for {signal.symbol}")
            return None
        
        # Execute order
        if signal.action == 'BUY':
            order_result = self.broker.execute_buy(signal.symbol, quantity, current_price)
        else:
            logger.warning(f"SELL signals not yet supported: {signal.symbol}")
            return None
        
        if order_result['status'] != 'FILLED':
            logger.warning(f"Order rejected: {order_result.get('reason')}")
            return None
        
        # Create trade record
        trade_data = {
            'trade_id': f"TRADE_{uuid.uuid4().hex[:12]}".upper(),
            'signal_id': signal.id,
            'symbol': signal.symbol,
            'side': signal.action,
            'entry_price': order_result['fill_price'],
            'quantity': quantity,
            'position_size': order_result['total_cost'],
            'stop_loss': signal.stop_loss,
            'take_profit': signal.target_price,
            'status': 'OPEN'
        }
        
        trade = self.trade_repo.create(trade_data)
        
        logger.info(f"Created trade {trade.trade_id} for {signal.symbol}")
        
        # Update signal status
        signal.status = 'EXECUTED'
        self.db.commit()
        
        return trade
    
    def update_open_trades(self, current_prices: Dict[str, float]):
        """Update all open trades with current prices"""
        open_trades = self.trade_repo.get_open_trades()
        
        for trade in open_trades:
            current_price = current_prices.get(trade.symbol)
            if not current_price:
                continue
            
            # Update current price and unrealized P&L
            if trade.side == 'BUY':
                unrealized_pnl = (current_price - trade.entry_price) * trade.quantity
            else:
                unrealized_pnl = (trade.entry_price - current_price) * trade.quantity
            
            updates = {
                'current_price': current_price,
                'unrealized_pnl': unrealized_pnl
            }
            
            # Check stop loss
            if trade.stop_loss and current_price <= trade.stop_loss:
                logger.info(f"Stop loss hit for {trade.trade_id}")
                self._close_trade(trade, current_price, 'STOP_LOSS')
                continue
            
            # Check take profit
            if trade.take_profit and current_price >= trade.take_profit:
                logger.info(f"Take profit hit for {trade.trade_id}")
                self._close_trade(trade, current_price, 'TAKE_PROFIT')
                continue
            
            self.trade_repo.update_trade(trade.trade_id, updates)
    
    def close_trade(self, trade_id: str, current_price: float, reason: str = 'MANUAL') -> Optional[Trade]:
        """Manually close a trade"""
        trade = self.trade_repo.get_by_id(trade_id)
        if not trade or trade.status != 'OPEN':
            logger.warning(f"Trade {trade_id} not found or not open")
            return None
        
        return self._close_trade(trade, current_price, reason)
    
    def _close_trade(self, trade: Trade, exit_price: float, reason: str) -> Trade:
        """Internal method to close a trade"""
        # Execute sell order
        order_result = self.broker.execute_sell(trade.symbol, trade.quantity, exit_price)
        
        if order_result['status'] == 'FILLED':
            # Update trade record
            trade = self.trade_repo.close_trade(
                trade.trade_id,
                order_result['fill_price'],
                reason
            )
            
            logger.info(f"Closed trade {trade.trade_id}: P&L ${trade.pnl:.2f}")
        
        return trade
    
    def _calculate_position_size(self, signal: Signal) -> float:
        """Calculate position size based on signal quality"""
        base_size = self.default_position_size
        
        # Adjust by tier
        tier_multipliers = {
            'PLATINUM': 2.0,
            'GOLD': 1.5,
            'SILVER': 1.0,
            'BRONZE': 0.5
        }
        multiplier = tier_multipliers.get(signal.tier, 1.0)
        
        # Adjust by confidence
        confidence_factor = signal.confidence / 100.0
        
        position_size = base_size * multiplier * confidence_factor
        
        # Cap at maximum
        return min(position_size, self.max_position_size)
    
    def get_open_positions_summary(self, current_prices: Dict[str, float]) -> Dict:
        """Get summary of all open positions"""
        open_trades = self.trade_repo.get_open_trades()
        
        positions = []
        total_unrealized_pnl = 0.0
        
        for trade in open_trades:
            current_price = current_prices.get(trade.symbol, trade.entry_price)
            unrealized_pnl = (current_price - trade.entry_price) * trade.quantity
            unrealized_pnl_percent = (unrealized_pnl / trade.position_size) * 100
            
            total_unrealized_pnl += unrealized_pnl
            
            positions.append({
                'trade_id': trade.trade_id,
                'symbol': trade.symbol,
                'quantity': trade.quantity,
                'entry_price': trade.entry_price,
                'current_price': current_price,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_percent': unrealized_pnl_percent,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit
            })
        
        return {
            'positions': positions,
            'total_positions': len(positions),
            'total_unrealized_pnl': total_unrealized_pnl
        }
