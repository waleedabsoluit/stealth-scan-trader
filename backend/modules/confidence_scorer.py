"""
Confidence Scorer Module
Aggregates subscores into a raw confidence percentage
"""
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np


class ConfidenceScorer:
    """Calculates confidence scores for trading signals"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.weights = config.get('weights', {
            'momentum': 0.25,
            'volume': 0.20,
            'technical': 0.20,
            'sentiment': 0.15,
            'risk': 0.20
        })
        self.tier_thresholds = config.get('tier_thresholds', {
            'PLATINUM': 85,
            'GOLD': 70,
            'SILVER': 50,
            'BRONZE': 30
        })
        
    def score(self, signal: Dict, modules_output: Dict) -> Dict:
        """Calculate confidence score for a signal"""
        # Gather all component scores
        component_scores = self._gather_component_scores(signal, modules_output)
        
        # Calculate raw confidence
        raw_confidence = self._calculate_raw_confidence(component_scores)
        
        # Apply adjustments
        adjusted_confidence = self._apply_adjustments(raw_confidence, signal, modules_output)
        
        # Determine tier
        tier = self._determine_tier(adjusted_confidence)
        
        # Calculate sub-scores
        sub_scores = self._calculate_subscores(component_scores)
        
        return {
            'raw_confidence': round(raw_confidence, 2),
            'adjusted_confidence': round(adjusted_confidence, 2),
            'tier': tier,
            'component_scores': component_scores,
            'sub_scores': sub_scores,
            'adjustments': self._get_adjustments(raw_confidence, adjusted_confidence),
            'confidence_factors': self._get_confidence_factors(component_scores),
            'timestamp': datetime.now().isoformat()
        }
        
    def _gather_component_scores(self, signal: Dict, modules_output: Dict) -> Dict:
        """Gather scores from all modules"""
        scores = {}
        
        # Momentum score from OBV/VWAP
        if 'obv_vwap' in modules_output:
            obv_data = modules_output['obv_vwap'].get('signals', {}).get(signal['symbol'], {})
            scores['momentum'] = obv_data.get('signal_strength', 0) * 100
            
        # Volume score from float churn
        if 'float_churn' in modules_output:
            churn_data = modules_output['float_churn'].get('float_churn', {}).get(signal['symbol'], {})
            scores['volume'] = churn_data.get('churn_score', 0)
            
        # Technical score
        scores['technical'] = self._calculate_technical_score(signal)
        
        # Sentiment score
        scores['sentiment'] = self._calculate_sentiment_score(signal)
        
        # Risk score (inverted - lower risk = higher score)
        if 'risk' in modules_output:
            risk_data = modules_output['risk'].get(signal['symbol'], {})
            risk_level = risk_data.get('overall_risk', 50)
            scores['risk'] = max(0, 100 - risk_level)
        else:
            scores['risk'] = 50  # Default neutral risk
            
        return scores
        
    def _calculate_raw_confidence(self, component_scores: Dict) -> float:
        """Calculate weighted average of component scores"""
        total_weight = 0
        weighted_sum = 0
        
        for component, score in component_scores.items():
            weight = self.weights.get(component, 0.1)
            weighted_sum += score * weight
            total_weight += weight
            
        if total_weight > 0:
            return weighted_sum / total_weight
        return 0
        
    def _apply_adjustments(self, raw_confidence: float, signal: Dict, 
                          modules_output: Dict) -> float:
        """Apply adjustments based on market conditions and risk factors"""
        adjusted = raw_confidence
        
        # Dilution penalty
        if 'dilution' in modules_output:
            dilution_data = modules_output['dilution'].get('dilution_analysis', {}).get(signal['symbol'], {})
            if dilution_data.get('risk_level') in ['HIGH', 'CRITICAL']:
                adjusted *= 0.7  # 30% penalty for high dilution risk
                
        # Squeeze bonus
        if 'squeeze' in modules_output:
            squeeze_data = modules_output['squeeze'].get('squeeze_analysis', {}).get(signal['symbol'], {})
            if squeeze_data.get('squeeze_potential') in ['HIGH', 'EXTREME']:
                adjusted *= 1.2  # 20% bonus for squeeze potential
                
        # Market hours adjustment
        market_session = signal.get('market_session', 'regular')
        if market_session == 'premarket':
            adjusted *= 0.9  # 10% penalty for premarket
        elif market_session == 'afterhours':
            adjusted *= 0.85  # 15% penalty for afterhours
            
        # Cap at 100
        return min(adjusted, 100)
        
    def _determine_tier(self, confidence: float) -> str:
        """Determine signal tier based on confidence"""
        for tier in ['PLATINUM', 'GOLD', 'SILVER', 'BRONZE']:
            if confidence >= self.tier_thresholds[tier]:
                return tier
        return 'UNRANKED'
        
    def _calculate_subscores(self, component_scores: Dict) -> Dict:
        """Calculate detailed sub-scores"""
        return {
            'momentum_quality': self._assess_momentum_quality(component_scores.get('momentum', 0)),
            'volume_quality': self._assess_volume_quality(component_scores.get('volume', 0)),
            'technical_quality': self._assess_technical_quality(component_scores.get('technical', 0)),
            'sentiment_quality': self._assess_sentiment_quality(component_scores.get('sentiment', 0)),
            'risk_quality': self._assess_risk_quality(component_scores.get('risk', 0))
        }
        
    def _calculate_technical_score(self, signal: Dict) -> float:
        """Calculate technical analysis score"""
        # Simulated technical score
        import random
        
        score = 0
        
        # RSI component
        rsi = signal.get('rsi', random.uniform(20, 80))
        if 30 <= rsi <= 70:
            score += 25
        elif 20 <= rsi <= 80:
            score += 15
            
        # Moving average component
        if signal.get('above_ma20', random.random() < 0.6):
            score += 25
            
        # Volume component
        if signal.get('volume_above_avg', random.random() < 0.5):
            score += 25
            
        # Pattern component
        if signal.get('bullish_pattern', random.random() < 0.3):
            score += 25
            
        return score
        
    def _calculate_sentiment_score(self, signal: Dict) -> float:
        """Calculate sentiment analysis score"""
        # Simulated sentiment score
        import random
        
        base_sentiment = random.uniform(30, 90)
        
        # Adjust for news
        if signal.get('recent_news', False):
            base_sentiment *= 1.1
            
        # Adjust for social mentions
        if signal.get('social_buzz', False):
            base_sentiment *= 1.05
            
        return min(base_sentiment, 100)
        
    def _assess_momentum_quality(self, score: float) -> str:
        """Assess quality of momentum"""
        if score >= 80:
            return 'STRONG'
        elif score >= 60:
            return 'MODERATE'
        elif score >= 40:
            return 'WEAK'
        else:
            return 'NEGATIVE'
            
    def _assess_volume_quality(self, score: float) -> str:
        """Assess quality of volume"""
        if score >= 75:
            return 'EXCEPTIONAL'
        elif score >= 50:
            return 'GOOD'
        elif score >= 25:
            return 'FAIR'
        else:
            return 'POOR'
            
    def _assess_technical_quality(self, score: float) -> str:
        """Assess quality of technical setup"""
        if score >= 75:
            return 'BULLISH'
        elif score >= 50:
            return 'NEUTRAL_BULLISH'
        elif score >= 25:
            return 'NEUTRAL'
        else:
            return 'BEARISH'
            
    def _assess_sentiment_quality(self, score: float) -> str:
        """Assess quality of sentiment"""
        if score >= 80:
            return 'VERY_POSITIVE'
        elif score >= 60:
            return 'POSITIVE'
        elif score >= 40:
            return 'NEUTRAL'
        else:
            return 'NEGATIVE'
            
    def _assess_risk_quality(self, score: float) -> str:
        """Assess risk quality (higher score = lower risk)"""
        if score >= 80:
            return 'VERY_LOW_RISK'
        elif score >= 60:
            return 'LOW_RISK'
        elif score >= 40:
            return 'MODERATE_RISK'
        else:
            return 'HIGH_RISK'
            
    def _get_adjustments(self, raw: float, adjusted: float) -> Dict:
        """Get list of adjustments applied"""
        difference = adjusted - raw
        percentage_change = (difference / raw * 100) if raw > 0 else 0
        
        return {
            'raw_score': round(raw, 2),
            'adjusted_score': round(adjusted, 2),
            'total_adjustment': round(difference, 2),
            'percentage_change': round(percentage_change, 2)
        }
        
    def _get_confidence_factors(self, component_scores: Dict) -> List[str]:
        """Get list of positive confidence factors"""
        factors = []
        
        if component_scores.get('momentum', 0) >= 70:
            factors.append('STRONG_MOMENTUM')
        if component_scores.get('volume', 0) >= 60:
            factors.append('HIGH_VOLUME')
        if component_scores.get('technical', 0) >= 65:
            factors.append('BULLISH_TECHNICALS')
        if component_scores.get('sentiment', 0) >= 70:
            factors.append('POSITIVE_SENTIMENT')
        if component_scores.get('risk', 0) >= 75:
            factors.append('LOW_RISK')
            
        return factors