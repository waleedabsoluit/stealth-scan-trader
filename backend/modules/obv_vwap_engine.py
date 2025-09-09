"""
OBV VWAP Engine Module
Purpose: Computes OBV slope and VWAP distance to judge momentum and stretched conditions
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class OBVVWAPEngine:
    """Engine for calculating On-Balance Volume slope and VWAP distance metrics."""
    
    def __init__(self, config: Dict):
        """
        Initialize OBV VWAP Engine with configuration.
        
        Args:
            config: Module configuration dictionary
        """
        self.lookback_period = config.get('lookback_period', 20)
        self.slope_threshold = config.get('slope_threshold', 0.5)
        self.vwap_stretch_threshold = config.get('vwap_stretch_threshold', 0.02)
        
    def analyze(self, market_data: Dict) -> Dict:
        """
        Analyze market data for OBV slope and VWAP distance.
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Analysis results with signals
        """
        results = {
            'signals': [],
            'metrics': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        symbols = market_data.get('symbols', [])
        
        for symbol in symbols:
            try:
                analysis = self._analyze_symbol(symbol, market_data)
                if analysis and self._is_signal(analysis):
                    results['signals'].append({
                        'symbol': symbol,
                        'obv_slope': analysis['obv_slope'],
                        'vwap_distance': analysis['vwap_distance'],
                        'momentum_score': analysis['momentum_score'],
                        'score': analysis['signal_strength'],
                        'timestamp': datetime.utcnow().isoformat()
                    })
            except Exception as e:
                # Log error but continue processing
                pass
        
        results['metrics'] = {
            'symbols_analyzed': len(symbols),
            'signals_generated': len(results['signals']),
            'avg_obv_slope': self._calculate_avg_metric(results['signals'], 'obv_slope'),
            'avg_vwap_distance': self._calculate_avg_metric(results['signals'], 'vwap_distance')
        }
        
        return results
    
    def _analyze_symbol(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """
        Analyze individual symbol for OBV and VWAP metrics.
        
        Args:
            symbol: Stock symbol
            market_data: Market data dictionary
            
        Returns:
            Analysis results or None
        """
        # Simulated calculation - in production, this would use real market data
        # This is a placeholder for actual OBV and VWAP calculations
        
        # Mock data for demonstration
        np.random.seed(hash(symbol) % 1000)  # Deterministic randomness per symbol
        
        # Calculate OBV slope (simplified)
        obv_values = np.cumsum(np.random.randn(self.lookback_period) * 1000)
        obv_slope = self._calculate_slope(obv_values)
        
        # Calculate VWAP distance (simplified)
        current_price = 100 + np.random.randn() * 10
        vwap = current_price * (1 + np.random.randn() * 0.01)
        vwap_distance = (current_price - vwap) / vwap
        
        # Calculate momentum score
        momentum_score = self._calculate_momentum_score(obv_slope, vwap_distance)
        
        # Calculate signal strength
        signal_strength = self._calculate_signal_strength(obv_slope, vwap_distance, momentum_score)
        
        return {
            'symbol': symbol,
            'obv_slope': obv_slope,
            'vwap_distance': vwap_distance,
            'momentum_score': momentum_score,
            'signal_strength': signal_strength,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_slope(self, values: np.ndarray) -> float:
        """
        Calculate the slope of values using linear regression.
        
        Args:
            values: Array of values
            
        Returns:
            Slope coefficient
        """
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]
        
        # Normalize slope to [-1, 1] range
        max_expected_slope = np.std(values) * 2
        if max_expected_slope > 0:
            normalized_slope = np.clip(slope / max_expected_slope, -1, 1)
        else:
            normalized_slope = 0.0
        
        return normalized_slope
    
    def _calculate_momentum_score(self, obv_slope: float, vwap_distance: float) -> float:
        """
        Calculate momentum score based on OBV slope and VWAP distance.
        
        Args:
            obv_slope: Normalized OBV slope
            vwap_distance: Distance from VWAP as percentage
            
        Returns:
            Momentum score (0-100)
        """
        # Positive OBV slope is bullish
        obv_component = max(0, obv_slope) * 50
        
        # Small positive VWAP distance is optimal (not too stretched)
        if 0 < vwap_distance < self.vwap_stretch_threshold:
            vwap_component = 50
        elif vwap_distance < 0:
            # Below VWAP can be good entry
            vwap_component = 30 * (1 - abs(vwap_distance) / 0.05)
        else:
            # Too stretched above VWAP
            vwap_component = max(0, 50 - (vwap_distance / self.vwap_stretch_threshold) * 50)
        
        momentum_score = obv_component + vwap_component
        return min(100, max(0, momentum_score))
    
    def _calculate_signal_strength(self, obv_slope: float, vwap_distance: float, 
                                  momentum_score: float) -> float:
        """
        Calculate overall signal strength.
        
        Args:
            obv_slope: Normalized OBV slope
            vwap_distance: Distance from VWAP
            momentum_score: Calculated momentum score
            
        Returns:
            Signal strength (0-100)
        """
        # Weight factors
        weights = {
            'obv': 0.4,
            'vwap': 0.3,
            'momentum': 0.3
        }
        
        # Calculate weighted score
        obv_score = max(0, obv_slope) * 100
        vwap_score = max(0, 100 - abs(vwap_distance) * 1000)
        
        signal_strength = (
            obv_score * weights['obv'] +
            vwap_score * weights['vwap'] +
            momentum_score * weights['momentum']
        )
        
        return min(100, max(0, signal_strength))
    
    def _is_signal(self, analysis: Dict) -> bool:
        """
        Determine if analysis results constitute a signal.
        
        Args:
            analysis: Analysis results dictionary
            
        Returns:
            True if signal criteria are met
        """
        return (
            analysis['obv_slope'] > self.slope_threshold and
            abs(analysis['vwap_distance']) < self.vwap_stretch_threshold * 2 and
            analysis['momentum_score'] > 60
        )
    
    def _calculate_avg_metric(self, signals: List[Dict], metric: str) -> float:
        """
        Calculate average value of a metric across signals.
        
        Args:
            signals: List of signal dictionaries
            metric: Metric name to average
            
        Returns:
            Average value or 0 if no signals
        """
        if not signals:
            return 0.0
        
        values = [s.get(metric, 0) for s in signals if metric in s]
        return sum(values) / len(values) if values else 0.0
    
    def set_universe(self, universe_provider):
        """Set the universe provider for the module."""
        self.universe_provider = universe_provider