"""
Squeeze Potential Scanner Module
Identifies contexts where shorts may be forced to cover (squeeze setups)
"""
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np


class SqueezePotentialScanner:
    """Detects potential short squeeze setups"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_short_interest = config.get('min_short_interest', 15.0)
        self.min_utilization = config.get('min_utilization', 85.0)
        self.min_days_to_cover = config.get('min_days_to_cover', 3.0)
        self.momentum_threshold = config.get('momentum_threshold', 0.2)
        
    def analyze(self, market_data: Dict) -> Dict:
        """Main analysis method for squeeze detection"""
        results = {}
        
        for symbol in market_data.get('symbols', []):
            analysis = self._analyze_symbol(symbol, market_data)
            if analysis:
                results[symbol] = analysis
                
        return {
            'squeeze_analysis': results,
            'high_potential': self._get_high_potential_squeezes(results),
            'squeeze_scores': self._rank_by_squeeze_score(results),
            'timestamp': datetime.now().isoformat()
        }
        
    def _analyze_symbol(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Analyze squeeze potential for a single symbol"""
        try:
            symbol_data = market_data.get('data', {}).get(symbol, {})
            
            # Get short interest data (simulated)
            short_metrics = self._get_short_metrics(symbol, symbol_data)
            
            # Calculate momentum indicators
            momentum = self._calculate_momentum(symbol_data)
            
            # Check for catalysts
            catalyst_score = self._evaluate_catalysts(symbol_data)
            
            # Calculate squeeze score
            squeeze_score = self._calculate_squeeze_score(
                short_metrics, momentum, catalyst_score
            )
            
            # Determine squeeze potential
            squeeze_potential = self._determine_potential(squeeze_score)
            
            return {
                'short_interest': short_metrics['short_interest'],
                'utilization': short_metrics['utilization'],
                'days_to_cover': short_metrics['days_to_cover'],
                'borrow_rate': short_metrics['borrow_rate'],
                'momentum_score': round(momentum, 2),
                'catalyst_score': round(catalyst_score, 2),
                'squeeze_score': round(squeeze_score, 2),
                'squeeze_potential': squeeze_potential,
                'setup_quality': self._evaluate_setup_quality(squeeze_score, short_metrics),
                'risk_factors': self._identify_risk_factors(short_metrics, symbol_data),
                'triggers': self._identify_triggers(momentum, catalyst_score)
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
            
    def _get_short_metrics(self, symbol: str, symbol_data: Dict) -> Dict:
        """Get or calculate short interest metrics"""
        # Simulated data - replace with actual data source
        import random
        
        return {
            'short_interest': random.uniform(5, 40),
            'utilization': random.uniform(60, 99),
            'days_to_cover': random.uniform(1, 10),
            'borrow_rate': random.uniform(5, 150),
            'shares_available': random.randint(1000, 1000000)
        }
        
    def _calculate_momentum(self, symbol_data: Dict) -> float:
        """Calculate momentum indicators for squeeze"""
        # Simulated momentum calculation
        import random
        
        price_change = symbol_data.get('change_percent', random.uniform(-10, 30))
        volume_ratio = symbol_data.get('volume', 1e6) / symbol_data.get('avg_volume', 1e6)
        
        # Combine price and volume momentum
        price_momentum = max(0, price_change / 100)
        volume_momentum = max(0, (volume_ratio - 1) / 5)
        
        return (price_momentum * 0.6 + volume_momentum * 0.4) * 100
        
    def _evaluate_catalysts(self, symbol_data: Dict) -> float:
        """Evaluate potential catalysts for squeeze"""
        # Simulated catalyst evaluation
        import random
        
        catalyst_score = 0
        
        # Check for news/events
        if random.random() < 0.3:  # Simulated news presence
            catalyst_score += 30
            
        # Check for technical breakout
        if random.random() < 0.4:  # Simulated breakout
            catalyst_score += 25
            
        # Check for insider buying
        if random.random() < 0.2:  # Simulated insider activity
            catalyst_score += 20
            
        # Check for earnings/FDA/contract news
        if random.random() < 0.25:  # Simulated major event
            catalyst_score += 25
            
        return min(catalyst_score, 100)
        
    def _calculate_squeeze_score(self, short_metrics: Dict, momentum: float, 
                                catalyst_score: float) -> float:
        """Calculate overall squeeze score"""
        # Weight components
        short_weight = 0.4
        momentum_weight = 0.35
        catalyst_weight = 0.25
        
        # Normalize short metrics
        short_score = 0
        if short_metrics['short_interest'] >= self.min_short_interest:
            short_score += 25
        if short_metrics['utilization'] >= self.min_utilization:
            short_score += 25
        if short_metrics['days_to_cover'] >= self.min_days_to_cover:
            short_score += 25
        if short_metrics['borrow_rate'] >= 30:
            short_score += 25
            
        # Calculate weighted score
        total_score = (
            short_score * short_weight +
            momentum * momentum_weight +
            catalyst_score * catalyst_weight
        )
        
        return min(total_score, 100)
        
    def _determine_potential(self, squeeze_score: float) -> str:
        """Determine squeeze potential level"""
        if squeeze_score >= 80:
            return 'EXTREME'
        elif squeeze_score >= 65:
            return 'HIGH'
        elif squeeze_score >= 45:
            return 'MODERATE'
        elif squeeze_score >= 25:
            return 'LOW'
        else:
            return 'MINIMAL'
            
    def _evaluate_setup_quality(self, squeeze_score: float, short_metrics: Dict) -> str:
        """Evaluate the quality of the squeeze setup"""
        quality_points = 0
        
        if squeeze_score >= 60:
            quality_points += 2
        if short_metrics['utilization'] >= 95:
            quality_points += 2
        if short_metrics['days_to_cover'] >= 5:
            quality_points += 1
        if short_metrics['borrow_rate'] >= 50:
            quality_points += 1
            
        if quality_points >= 5:
            return 'PREMIUM'
        elif quality_points >= 3:
            return 'GOOD'
        elif quality_points >= 1:
            return 'FAIR'
        else:
            return 'POOR'
            
    def _identify_risk_factors(self, short_metrics: Dict, symbol_data: Dict) -> List[str]:
        """Identify risk factors for the squeeze setup"""
        risks = []
        
        if short_metrics['shares_available'] > 500000:
            risks.append('HIGH_SHARE_AVAILABILITY')
            
        if short_metrics['borrow_rate'] < 10:
            risks.append('LOW_BORROW_COST')
            
        market_cap = symbol_data.get('market_cap', 0)
        if market_cap > 10e9:
            risks.append('LARGE_CAP')
            
        if symbol_data.get('avg_volume', 0) < 1e6:
            risks.append('LOW_LIQUIDITY')
            
        return risks
        
    def _identify_triggers(self, momentum: float, catalyst_score: float) -> List[str]:
        """Identify potential squeeze triggers"""
        triggers = []
        
        if momentum > 50:
            triggers.append('MOMENTUM_SURGE')
            
        if catalyst_score > 60:
            triggers.append('CATALYST_PRESENT')
            
        # Add more trigger conditions
        import random
        if random.random() < 0.3:
            triggers.append('TECHNICAL_BREAKOUT')
        if random.random() < 0.2:
            triggers.append('OPTIONS_FLOW')
            
        return triggers
        
    def _get_high_potential_squeezes(self, results: Dict) -> List[Dict]:
        """Get symbols with high squeeze potential"""
        high_potential = []
        for symbol, data in results.items():
            if data.get('squeeze_potential') in ['HIGH', 'EXTREME']:
                high_potential.append({
                    'symbol': symbol,
                    'score': data['squeeze_score'],
                    'potential': data['squeeze_potential'],
                    'setup_quality': data['setup_quality'],
                    'triggers': data['triggers']
                })
        return sorted(high_potential, key=lambda x: x['score'], reverse=True)
        
    def _rank_by_squeeze_score(self, results: Dict) -> List[Dict]:
        """Rank all symbols by squeeze score"""
        ranked = []
        for symbol, data in results.items():
            ranked.append({
                'symbol': symbol,
                'score': data['squeeze_score'],
                'short_interest': data['short_interest'],
                'utilization': data['utilization']
            })
        return sorted(ranked, key=lambda x: x['score'], reverse=True)[:20]