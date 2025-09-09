"""
Float Churn Module
Estimates how quickly the float is turning over (liquidity/attention proxy)
"""
from typing import Dict, Optional
import numpy as np
from datetime import datetime, timedelta


class FloatChurnEngine:
    """Computes float churn ratio to measure liquidity and attention"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.lookback_days = config.get('lookback_days', 5)
        self.churn_threshold = config.get('churn_threshold', 0.3)
        self.volume_multiplier = config.get('volume_multiplier', 1.5)
        
    def analyze(self, market_data: Dict) -> Dict:
        """Main analysis method for float churn calculation"""
        results = {}
        
        for symbol in market_data.get('symbols', []):
            analysis = self._analyze_symbol(symbol, market_data)
            if analysis:
                results[symbol] = analysis
                
        return {
            'float_churn': results,
            'high_churn_symbols': self._get_high_churn_symbols(results),
            'timestamp': datetime.now().isoformat()
        }
        
    def _analyze_symbol(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Calculate float churn for a single symbol"""
        try:
            # Simulated data - replace with actual market data
            symbol_data = market_data.get('data', {}).get(symbol, {})
            
            # Get volume and float data
            avg_volume = symbol_data.get('avg_volume', np.random.uniform(1e6, 1e8))
            float_shares = symbol_data.get('float', np.random.uniform(1e7, 1e9))
            current_volume = symbol_data.get('volume', np.random.uniform(1e6, 5e7))
            
            # Calculate churn metrics
            daily_churn = current_volume / float_shares if float_shares > 0 else 0
            avg_daily_churn = avg_volume / float_shares if float_shares > 0 else 0
            relative_churn = daily_churn / avg_daily_churn if avg_daily_churn > 0 else 0
            
            # Calculate churn score
            churn_score = self._calculate_churn_score(
                daily_churn, relative_churn, current_volume, avg_volume
            )
            
            return {
                'daily_churn': round(daily_churn, 4),
                'avg_daily_churn': round(avg_daily_churn, 4),
                'relative_churn': round(relative_churn, 2),
                'churn_score': round(churn_score, 2),
                'float_shares': float_shares,
                'current_volume': current_volume,
                'is_high_churn': daily_churn > self.churn_threshold,
                'liquidity_rating': self._get_liquidity_rating(churn_score)
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
            
    def _calculate_churn_score(self, daily_churn: float, relative_churn: float,
                               current_volume: float, avg_volume: float) -> float:
        """Calculate composite churn score"""
        # Weight factors
        churn_weight = 0.4
        relative_weight = 0.3
        volume_weight = 0.3
        
        # Normalize scores
        churn_component = min(daily_churn / self.churn_threshold, 2.0) * churn_weight
        relative_component = min(relative_churn, 3.0) / 3.0 * relative_weight
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        volume_component = min(volume_ratio, 5.0) / 5.0 * volume_weight
        
        return (churn_component + relative_component + volume_component) * 100
        
    def _get_liquidity_rating(self, churn_score: float) -> str:
        """Determine liquidity rating based on churn score"""
        if churn_score >= 80:
            return 'EXTREME'
        elif churn_score >= 60:
            return 'HIGH'
        elif churn_score >= 40:
            return 'MODERATE'
        elif churn_score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
            
    def _get_high_churn_symbols(self, results: Dict) -> list:
        """Get list of symbols with high churn"""
        high_churn = []
        for symbol, data in results.items():
            if data.get('is_high_churn'):
                high_churn.append({
                    'symbol': symbol,
                    'churn': data['daily_churn'],
                    'score': data['churn_score']
                })
        return sorted(high_churn, key=lambda x: x['score'], reverse=True)