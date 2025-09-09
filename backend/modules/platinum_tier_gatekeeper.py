"""
Platinum Tier Gatekeeper Module
Strict risk gate for top-tier signals
"""
from typing import Dict, List, Optional
from datetime import datetime


class PlatinumTierGatekeeper:
    """Enforces strict criteria for platinum tier signals"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_confidence = config.get('min_confidence', 85)
        self.max_rsi = config.get('max_rsi', 75)
        self.min_rsi = config.get('min_rsi', 25)
        self.max_dilution_risk = config.get('max_dilution_risk', 30)
        self.min_volume_ratio = config.get('min_volume_ratio', 2.0)
        self.max_spread = config.get('max_spread', 0.02)  # 2% max spread
        self.min_liquidity = config.get('min_liquidity', 1e6)  # $1M daily volume
        
    def validate(self, signal: Dict, modules_output: Dict) -> Dict:
        """Validate signal against platinum criteria"""
        validations = []
        passed = True
        rejection_reasons = []
        
        # Confidence check
        confidence_check = self._check_confidence(signal)
        validations.append(confidence_check)
        if not confidence_check['passed']:
            passed = False
            rejection_reasons.append(confidence_check['reason'])
            
        # RSI check
        rsi_check = self._check_rsi(signal)
        validations.append(rsi_check)
        if not rsi_check['passed']:
            passed = False
            rejection_reasons.append(rsi_check['reason'])
            
        # Dilution check
        dilution_check = self._check_dilution(signal, modules_output)
        validations.append(dilution_check)
        if not dilution_check['passed']:
            passed = False
            rejection_reasons.append(dilution_check['reason'])
            
        # Volume check
        volume_check = self._check_volume(signal)
        validations.append(volume_check)
        if not volume_check['passed']:
            passed = False
            rejection_reasons.append(volume_check['reason'])
            
        # Liquidity check
        liquidity_check = self._check_liquidity(signal)
        validations.append(liquidity_check)
        if not liquidity_check['passed']:
            passed = False
            rejection_reasons.append(liquidity_check['reason'])
            
        # Float check
        float_check = self._check_float(signal, modules_output)
        validations.append(float_check)
        if not float_check['passed']:
            passed = False
            rejection_reasons.append(float_check['reason'])
            
        # Pattern check
        pattern_check = self._check_patterns(signal)
        validations.append(pattern_check)
        if not pattern_check['passed']:
            passed = False
            rejection_reasons.append(pattern_check['reason'])
            
        # Calculate quality score
        quality_score = self._calculate_quality_score(validations)
        
        return {
            'passed': passed,
            'quality_score': round(quality_score, 2),
            'validations': validations,
            'rejection_reasons': rejection_reasons,
            'platinum_eligible': passed and quality_score >= 80,
            'recommendation': self._get_recommendation(passed, quality_score),
            'timestamp': datetime.now().isoformat()
        }
        
    def _check_confidence(self, signal: Dict) -> Dict:
        """Check confidence meets minimum threshold"""
        confidence = signal.get('confidence', 0)
        passed = confidence >= self.min_confidence
        
        return {
            'check': 'confidence',
            'passed': passed,
            'value': confidence,
            'threshold': self.min_confidence,
            'reason': f'Confidence {confidence}% below {self.min_confidence}%' if not passed else None
        }
        
    def _check_rsi(self, signal: Dict) -> Dict:
        """Check RSI is not overbought/oversold"""
        rsi = signal.get('rsi', 50)
        passed = self.min_rsi <= rsi <= self.max_rsi
        
        reason = None
        if rsi > self.max_rsi:
            reason = f'RSI {rsi} overbought (>{self.max_rsi})'
        elif rsi < self.min_rsi:
            reason = f'RSI {rsi} oversold (<{self.min_rsi})'
            
        return {
            'check': 'rsi',
            'passed': passed,
            'value': rsi,
            'threshold': f'{self.min_rsi}-{self.max_rsi}',
            'reason': reason
        }
        
    def _check_dilution(self, signal: Dict, modules_output: Dict) -> Dict:
        """Check dilution risk is acceptable"""
        dilution_data = modules_output.get('dilution', {}).get('dilution_analysis', {})
        symbol_dilution = dilution_data.get(signal['symbol'], {})
        risk_score = symbol_dilution.get('risk_score', 0)
        
        passed = risk_score <= self.max_dilution_risk
        
        return {
            'check': 'dilution',
            'passed': passed,
            'value': risk_score,
            'threshold': self.max_dilution_risk,
            'reason': f'Dilution risk {risk_score} exceeds {self.max_dilution_risk}' if not passed else None
        }
        
    def _check_volume(self, signal: Dict) -> Dict:
        """Check volume meets minimum requirements"""
        volume_ratio = signal.get('volume', 0) / signal.get('avg_volume', 1)
        passed = volume_ratio >= self.min_volume_ratio
        
        return {
            'check': 'volume',
            'passed': passed,
            'value': round(volume_ratio, 2),
            'threshold': self.min_volume_ratio,
            'reason': f'Volume ratio {volume_ratio:.2f} below {self.min_volume_ratio}' if not passed else None
        }
        
    def _check_liquidity(self, signal: Dict) -> Dict:
        """Check liquidity meets minimum requirements"""
        dollar_volume = signal.get('volume', 0) * signal.get('price', 0)
        passed = dollar_volume >= self.min_liquidity
        
        return {
            'check': 'liquidity',
            'passed': passed,
            'value': dollar_volume,
            'threshold': self.min_liquidity,
            'reason': f'Dollar volume ${dollar_volume:,.0f} below ${self.min_liquidity:,.0f}' if not passed else None
        }
        
    def _check_float(self, signal: Dict, modules_output: Dict) -> Dict:
        """Check float characteristics are acceptable"""
        float_data = modules_output.get('float_churn', {}).get('float_churn', {})
        symbol_float = float_data.get(signal['symbol'], {})
        
        # Check for micro float (too risky)
        float_shares = symbol_float.get('float_shares', 1e9)
        micro_float = float_shares < 10e6  # Less than 10M shares
        
        passed = not micro_float
        
        return {
            'check': 'float',
            'passed': passed,
            'value': float_shares,
            'threshold': '10M minimum',
            'reason': f'Micro float {float_shares/1e6:.1f}M shares' if not passed else None
        }
        
    def _check_patterns(self, signal: Dict) -> Dict:
        """Check for negative patterns"""
        # Check for pump and dump patterns
        price_spike = signal.get('price_change_1d', 0) > 50  # >50% in a day
        
        # Check for gap and crap pattern
        gap_up = signal.get('gap_percent', 0) > 20
        fading = signal.get('price', 0) < signal.get('open', 0)
        gap_and_crap = gap_up and fading
        
        passed = not (price_spike or gap_and_crap)
        
        reason = None
        if price_spike:
            reason = 'Potential pump pattern detected'
        elif gap_and_crap:
            reason = 'Gap and fade pattern detected'
            
        return {
            'check': 'patterns',
            'passed': passed,
            'value': 'clean' if passed else 'suspicious',
            'threshold': 'no negative patterns',
            'reason': reason
        }
        
    def _calculate_quality_score(self, validations: List[Dict]) -> float:
        """Calculate overall quality score"""
        total_checks = len(validations)
        passed_checks = sum(1 for v in validations if v['passed'])
        
        # Base score from passed checks
        base_score = (passed_checks / total_checks) * 100
        
        # Apply penalties for critical failures
        critical_checks = ['confidence', 'dilution', 'patterns']
        for validation in validations:
            if validation['check'] in critical_checks and not validation['passed']:
                base_score *= 0.8  # 20% penalty for each critical failure
                
        return min(base_score, 100)
        
    def _get_recommendation(self, passed: bool, quality_score: float) -> str:
        """Get trading recommendation based on validation"""
        if not passed:
            return 'REJECT'
        elif quality_score >= 90:
            return 'STRONG_BUY'
        elif quality_score >= 80:
            return 'BUY'
        elif quality_score >= 70:
            return 'WATCH'
        else:
            return 'PASS'