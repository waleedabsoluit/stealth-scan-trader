"""
Risk Engine Module
Purpose: Central place to combine and normalize risk dimensions for decisions/logging
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk level classifications."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


@dataclass
class RiskMetrics:
    """Container for risk metrics."""
    portfolio_risk: float
    position_risk: float
    market_risk: float
    correlation_risk: float
    liquidity_risk: float
    overall_risk: float
    risk_level: RiskLevel
    max_position_size: float
    stop_loss: float
    take_profit: float


class RiskEngine:
    """Central risk management engine for the trading system."""
    
    def __init__(self, config: Dict):
        """
        Initialize Risk Engine with configuration.
        
        Args:
            config: Risk configuration dictionary
        """
        self.max_portfolio_risk = config.get('max_portfolio_risk', 0.06)
        self.max_correlation = config.get('max_correlation', 0.7)
        self.vix_threshold = config.get('vix_threshold', 30)
        self.position_sizing = config.get('position_sizing', 'kelly')
        
        # Risk thresholds
        self.risk_thresholds = {
            'low': 0.02,
            'medium': 0.04,
            'high': 0.06,
            'extreme': 0.10
        }
        
        # Position size limits
        self.position_limits = {
            'min_size': 0.001,
            'max_size': 0.1,
            'max_positions': 10
        }
    
    def assess_risk(self, signal: Dict, portfolio: Dict, market_data: Dict) -> RiskMetrics:
        """
        Comprehensive risk assessment for a trading signal.
        
        Args:
            signal: Trading signal dictionary
            portfolio: Current portfolio state
            market_data: Market conditions data
            
        Returns:
            RiskMetrics object with all risk dimensions
        """
        # Calculate individual risk components
        portfolio_risk = self._calculate_portfolio_risk(portfolio)
        position_risk = self._calculate_position_risk(signal, market_data)
        market_risk = self._calculate_market_risk(market_data)
        correlation_risk = self._calculate_correlation_risk(signal, portfolio)
        liquidity_risk = self._calculate_liquidity_risk(signal, market_data)
        
        # Calculate overall risk
        overall_risk = self._aggregate_risks({
            'portfolio': portfolio_risk,
            'position': position_risk,
            'market': market_risk,
            'correlation': correlation_risk,
            'liquidity': liquidity_risk
        })
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_risk)
        
        # Calculate position parameters
        max_position_size = self._calculate_max_position_size(
            overall_risk, portfolio, signal
        )
        stop_loss = self._calculate_stop_loss(signal, market_data, risk_level)
        take_profit = self._calculate_take_profit(signal, market_data, risk_level)
        
        return RiskMetrics(
            portfolio_risk=portfolio_risk,
            position_risk=position_risk,
            market_risk=market_risk,
            correlation_risk=correlation_risk,
            liquidity_risk=liquidity_risk,
            overall_risk=overall_risk,
            risk_level=risk_level,
            max_position_size=max_position_size,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    
    def _calculate_portfolio_risk(self, portfolio: Dict) -> float:
        """
        Calculate current portfolio risk.
        
        Args:
            portfolio: Portfolio state dictionary
            
        Returns:
            Portfolio risk score (0-1)
        """
        positions = portfolio.get('positions', [])
        if not positions:
            return 0.0
        
        total_value = portfolio.get('total_value', 100000)
        position_values = [p.get('value', 0) for p in positions]
        
        # Calculate concentration risk
        max_position = max(position_values) if position_values else 0
        concentration_risk = max_position / total_value if total_value > 0 else 0
        
        # Calculate exposure risk
        total_exposure = sum(position_values)
        exposure_risk = total_exposure / total_value if total_value > 0 else 0
        
        # Calculate drawdown risk
        current_drawdown = portfolio.get('drawdown', 0)
        max_drawdown = portfolio.get('max_drawdown', 0.1)
        drawdown_risk = abs(current_drawdown / max_drawdown) if max_drawdown != 0 else 0
        
        # Weighted portfolio risk
        portfolio_risk = (
            concentration_risk * 0.3 +
            exposure_risk * 0.4 +
            drawdown_risk * 0.3
        )
        
        return min(1.0, max(0.0, portfolio_risk))
    
    def _calculate_position_risk(self, signal: Dict, market_data: Dict) -> float:
        """
        Calculate risk for a specific position.
        
        Args:
            signal: Trading signal
            market_data: Market data
            
        Returns:
            Position risk score (0-1)
        """
        symbol = signal.get('symbol', '')
        
        # Volatility risk
        volatility = market_data.get('volatility', {}).get(symbol, 0.02)
        vol_risk = min(1.0, volatility / 0.5)  # 50% volatility = max risk
        
        # Momentum risk (too extended)
        momentum = signal.get('modules', {}).get('obv_vwap', {}).get('momentum_score', 50)
        momentum_risk = 0 if momentum < 80 else (momentum - 80) / 20
        
        # News/catalyst risk
        catalyst_age = signal.get('modules', {}).get('catalyst_latency', {}).get('days_since', 0)
        catalyst_risk = min(1.0, catalyst_age / 30)  # 30+ days = max risk
        
        # Weighted position risk
        position_risk = (
            vol_risk * 0.5 +
            momentum_risk * 0.3 +
            catalyst_risk * 0.2
        )
        
        return min(1.0, max(0.0, position_risk))
    
    def _calculate_market_risk(self, market_data: Dict) -> float:
        """
        Calculate overall market risk.
        
        Args:
            market_data: Market conditions
            
        Returns:
            Market risk score (0-1)
        """
        # VIX level risk
        vix = market_data.get('vix', 15)
        vix_risk = min(1.0, vix / self.vix_threshold)
        
        # Market trend risk
        market_trend = market_data.get('trend', 'neutral')
        trend_risk = {
            'strong_up': 0.2,
            'up': 0.3,
            'neutral': 0.5,
            'down': 0.7,
            'strong_down': 0.9
        }.get(market_trend, 0.5)
        
        # Volume risk (low volume = higher risk)
        relative_volume = market_data.get('relative_volume', 1.0)
        volume_risk = max(0, 1.0 - relative_volume)
        
        # Weighted market risk
        market_risk = (
            vix_risk * 0.4 +
            trend_risk * 0.3 +
            volume_risk * 0.3
        )
        
        return min(1.0, max(0.0, market_risk))
    
    def _calculate_correlation_risk(self, signal: Dict, portfolio: Dict) -> float:
        """
        Calculate correlation risk with existing positions.
        
        Args:
            signal: Trading signal
            portfolio: Current portfolio
            
        Returns:
            Correlation risk score (0-1)
        """
        symbol = signal.get('symbol', '')
        positions = portfolio.get('positions', [])
        
        if not positions:
            return 0.0
        
        # Simplified correlation calculation
        # In production, this would use actual correlation matrices
        sector = signal.get('sector', 'unknown')
        same_sector_positions = [
            p for p in positions 
            if p.get('sector') == sector
        ]
        
        # Sector concentration risk
        sector_concentration = len(same_sector_positions) / max(1, len(positions))
        
        # Direct correlation estimate
        correlations = []
        for position in positions:
            if position.get('symbol') == symbol:
                correlations.append(1.0)  # Same symbol = perfect correlation
            elif position.get('sector') == sector:
                correlations.append(0.7)  # Same sector = high correlation
            else:
                correlations.append(0.3)  # Different sector = low correlation
        
        avg_correlation = sum(correlations) / len(correlations) if correlations else 0
        
        # Weighted correlation risk
        correlation_risk = (
            sector_concentration * 0.4 +
            avg_correlation * 0.6
        )
        
        return min(1.0, max(0.0, correlation_risk))
    
    def _calculate_liquidity_risk(self, signal: Dict, market_data: Dict) -> float:
        """
        Calculate liquidity risk for the position.
        
        Args:
            signal: Trading signal
            market_data: Market data
            
        Returns:
            Liquidity risk score (0-1)
        """
        symbol = signal.get('symbol', '')
        
        # Average volume
        avg_volume = market_data.get('avg_volume', {}).get(symbol, 1000000)
        volume_threshold = 500000  # Minimum acceptable volume
        
        if avg_volume < volume_threshold:
            volume_risk = 1.0 - (avg_volume / volume_threshold)
        else:
            volume_risk = 0.0
        
        # Bid-ask spread
        spread = market_data.get('spread', {}).get(symbol, 0.01)
        spread_risk = min(1.0, spread / 0.05)  # 5% spread = max risk
        
        # Float turnover
        float_churn = signal.get('modules', {}).get('float_churn', {}).get('turnover_rate', 1.0)
        float_risk = max(0, 1.0 - float_churn)
        
        # Weighted liquidity risk
        liquidity_risk = (
            volume_risk * 0.4 +
            spread_risk * 0.3 +
            float_risk * 0.3
        )
        
        return min(1.0, max(0.0, liquidity_risk))
    
    def _aggregate_risks(self, risks: Dict[str, float]) -> float:
        """
        Aggregate multiple risk dimensions into overall risk.
        
        Args:
            risks: Dictionary of risk components
            
        Returns:
            Overall risk score (0-1)
        """
        # Risk weights
        weights = {
            'portfolio': 0.25,
            'position': 0.20,
            'market': 0.25,
            'correlation': 0.15,
            'liquidity': 0.15
        }
        
        # Calculate weighted average
        weighted_sum = sum(
            risks.get(risk_type, 0) * weight 
            for risk_type, weight in weights.items()
        )
        
        # Apply non-linear scaling for extreme risks
        if weighted_sum > 0.7:
            # Amplify high risk
            overall_risk = 0.7 + (weighted_sum - 0.7) * 1.5
        else:
            overall_risk = weighted_sum
        
        return min(1.0, max(0.0, overall_risk))
    
    def _determine_risk_level(self, overall_risk: float) -> RiskLevel:
        """
        Determine risk level category.
        
        Args:
            overall_risk: Overall risk score
            
        Returns:
            RiskLevel enum
        """
        if overall_risk < self.risk_thresholds['low']:
            return RiskLevel.LOW
        elif overall_risk < self.risk_thresholds['medium']:
            return RiskLevel.MEDIUM
        elif overall_risk < self.risk_thresholds['high']:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME
    
    def _calculate_max_position_size(self, overall_risk: float, 
                                    portfolio: Dict, signal: Dict) -> float:
        """
        Calculate maximum allowed position size based on risk.
        
        Args:
            overall_risk: Overall risk score
            portfolio: Portfolio state
            signal: Trading signal
            
        Returns:
            Maximum position size as fraction of portfolio
        """
        base_size = self.position_limits['max_size']
        
        # Reduce size based on risk
        risk_multiplier = max(0.1, 1.0 - overall_risk)
        
        # Kelly criterion adjustment
        if self.position_sizing == 'kelly':
            win_rate = portfolio.get('win_rate', 0.5)
            avg_win = portfolio.get('avg_win', 0.02)
            avg_loss = portfolio.get('avg_loss', 0.01)
            
            if avg_loss > 0:
                kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                kelly_fraction = min(0.25, max(0, kelly_fraction))  # Cap at 25%
            else:
                kelly_fraction = 0.02
            
            base_size = min(base_size, kelly_fraction)
        
        # Confidence adjustment
        confidence = signal.get('confidence', 50) / 100
        confidence_multiplier = 0.5 + confidence * 0.5
        
        # Final position size
        max_size = base_size * risk_multiplier * confidence_multiplier
        
        return min(self.position_limits['max_size'], 
                  max(self.position_limits['min_size'], max_size))
    
    def _calculate_stop_loss(self, signal: Dict, market_data: Dict, 
                            risk_level: RiskLevel) -> float:
        """
        Calculate stop loss level.
        
        Args:
            signal: Trading signal
            market_data: Market data
            risk_level: Current risk level
            
        Returns:
            Stop loss percentage
        """
        # Base stop loss by risk level
        base_stops = {
            RiskLevel.LOW: 0.05,
            RiskLevel.MEDIUM: 0.03,
            RiskLevel.HIGH: 0.02,
            RiskLevel.EXTREME: 0.01
        }
        
        base_stop = base_stops.get(risk_level, 0.03)
        
        # Adjust for volatility
        symbol = signal.get('symbol', '')
        volatility = market_data.get('volatility', {}).get(symbol, 0.02)
        volatility_multiplier = 1 + (volatility - 0.02) * 2
        
        stop_loss = base_stop * volatility_multiplier
        
        return min(0.1, max(0.005, stop_loss))  # 0.5% to 10%
    
    def _calculate_take_profit(self, signal: Dict, market_data: Dict, 
                              risk_level: RiskLevel) -> float:
        """
        Calculate take profit level.
        
        Args:
            signal: Trading signal
            market_data: Market data
            risk_level: Current risk level
            
        Returns:
            Take profit percentage
        """
        # Risk-reward ratios by risk level
        risk_reward_ratios = {
            RiskLevel.LOW: 3.0,
            RiskLevel.MEDIUM: 2.5,
            RiskLevel.HIGH: 2.0,
            RiskLevel.EXTREME: 1.5
        }
        
        ratio = risk_reward_ratios.get(risk_level, 2.0)
        
        # Get stop loss for ratio calculation
        stop_loss = self._calculate_stop_loss(signal, market_data, risk_level)
        
        # Calculate take profit
        take_profit = stop_loss * ratio
        
        # Adjust for momentum
        momentum = signal.get('modules', {}).get('obv_vwap', {}).get('momentum_score', 50)
        if momentum > 80:
            take_profit *= 1.2  # Extend profit target for strong momentum
        
        return min(0.5, max(0.01, take_profit))  # 1% to 50%