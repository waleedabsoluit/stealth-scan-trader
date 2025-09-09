"""
Dilution Detector Module
Flags dilution risk from shelf/ATM activity to avoid fragile runners
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re


class DilutionDetector:
    """Detects potential dilution risks from SEC filings and corporate actions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.lookback_days = config.get('lookback_days', 90)
        self.shelf_threshold = config.get('shelf_threshold_millions', 50)
        self.atm_alert_threshold = config.get('atm_alert_threshold', 0.2)
        
        # Risk keywords for filing analysis
        self.dilution_keywords = [
            'shelf registration', 'at-the-market', 'ATM',
            'direct offering', 'private placement', 'warrant',
            'convertible', 'equity line', 'common stock purchase'
        ]
        
    def analyze(self, market_data: Dict, filings_data: Dict = None) -> Dict:
        """Main analysis method for dilution detection"""
        results = {}
        
        for symbol in market_data.get('symbols', []):
            analysis = self._analyze_symbol(symbol, market_data, filings_data)
            if analysis:
                results[symbol] = analysis
                
        return {
            'dilution_analysis': results,
            'high_risk_symbols': self._get_high_risk_symbols(results),
            'recent_shelfs': self._get_recent_shelfs(results),
            'timestamp': datetime.now().isoformat()
        }
        
    def _analyze_symbol(self, symbol: str, market_data: Dict, 
                       filings_data: Optional[Dict]) -> Optional[Dict]:
        """Analyze dilution risk for a single symbol"""
        try:
            # Get market cap for context
            symbol_data = market_data.get('data', {}).get(symbol, {})
            market_cap = symbol_data.get('market_cap', 1e9)
            
            # Check for recent filings
            filing_risk = self._check_filings(symbol, filings_data) if filings_data else {}
            
            # Check for ATM activity patterns
            atm_risk = self._detect_atm_patterns(symbol, market_data)
            
            # Calculate overall dilution risk
            risk_score = self._calculate_risk_score(filing_risk, atm_risk, market_cap)
            
            return {
                'risk_score': round(risk_score, 2),
                'risk_level': self._get_risk_level(risk_score),
                'shelf_active': filing_risk.get('shelf_active', False),
                'shelf_amount': filing_risk.get('shelf_amount', 0),
                'atm_detected': atm_risk.get('detected', False),
                'atm_probability': atm_risk.get('probability', 0),
                'recent_filings': filing_risk.get('recent_filings', []),
                'market_cap': market_cap,
                'dilution_ratio': self._calculate_dilution_ratio(
                    filing_risk.get('shelf_amount', 0), market_cap
                ),
                'flags': self._generate_flags(filing_risk, atm_risk)
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
            
    def _check_filings(self, symbol: str, filings_data: Optional[Dict]) -> Dict:
        """Check SEC filings for dilution indicators"""
        if not filings_data:
            # Simulated filing data
            import random
            has_shelf = random.random() < 0.2
            return {
                'shelf_active': has_shelf,
                'shelf_amount': random.uniform(10, 200) * 1e6 if has_shelf else 0,
                'recent_filings': ['S-3'] if has_shelf else []
            }
            
        result = {
            'shelf_active': False,
            'shelf_amount': 0,
            'recent_filings': []
        }
        
        symbol_filings = filings_data.get(symbol, [])
        for filing in symbol_filings:
            # Check filing date
            filing_date = filing.get('date')
            if self._is_recent(filing_date):
                # Check for dilution keywords
                if self._contains_dilution_keywords(filing.get('text', '')):
                    result['shelf_active'] = True
                    result['shelf_amount'] = max(
                        result['shelf_amount'],
                        self._extract_amount(filing.get('text', ''))
                    )
                    result['recent_filings'].append(filing.get('type', 'Unknown'))
                    
        return result
        
    def _detect_atm_patterns(self, symbol: str, market_data: Dict) -> Dict:
        """Detect ATM offering patterns from trading data"""
        # Simulated ATM detection
        import random
        
        symbol_data = market_data.get('data', {}).get(symbol, {})
        volume = symbol_data.get('volume', 0)
        avg_volume = symbol_data.get('avg_volume', 1)
        
        # Look for volume patterns indicative of ATM
        volume_spike = volume / avg_volume if avg_volume > 0 else 1
        
        # Simulated detection logic
        atm_probability = min(volume_spike * 0.1 * random.random(), 1.0)
        
        return {
            'detected': atm_probability > self.atm_alert_threshold,
            'probability': round(atm_probability, 3),
            'volume_spike': round(volume_spike, 2)
        }
        
    def _calculate_risk_score(self, filing_risk: Dict, atm_risk: Dict, 
                             market_cap: float) -> float:
        """Calculate overall dilution risk score"""
        score = 0.0
        
        # Filing-based risk (0-50 points)
        if filing_risk.get('shelf_active'):
            dilution_ratio = filing_risk.get('shelf_amount', 0) / market_cap
            score += min(dilution_ratio * 100, 50)
            
        # ATM risk (0-30 points)
        score += atm_risk.get('probability', 0) * 30
        
        # Recent filing activity (0-20 points)
        recent_count = len(filing_risk.get('recent_filings', []))
        score += min(recent_count * 5, 20)
        
        return min(score, 100)
        
    def _calculate_dilution_ratio(self, shelf_amount: float, market_cap: float) -> float:
        """Calculate potential dilution as percentage of market cap"""
        if market_cap <= 0:
            return 0
        return round((shelf_amount / market_cap) * 100, 2)
        
    def _get_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score >= 70:
            return 'CRITICAL'
        elif risk_score >= 50:
            return 'HIGH'
        elif risk_score >= 30:
            return 'MODERATE'
        elif risk_score >= 10:
            return 'LOW'
        else:
            return 'MINIMAL'
            
    def _generate_flags(self, filing_risk: Dict, atm_risk: Dict) -> List[str]:
        """Generate warning flags based on risk factors"""
        flags = []
        
        if filing_risk.get('shelf_active'):
            flags.append('ACTIVE_SHELF')
            
        if filing_risk.get('shelf_amount', 0) > self.shelf_threshold * 1e6:
            flags.append('LARGE_SHELF')
            
        if atm_risk.get('detected'):
            flags.append('ATM_DETECTED')
            
        if len(filing_risk.get('recent_filings', [])) > 2:
            flags.append('FREQUENT_FILINGS')
            
        return flags
        
    def _get_high_risk_symbols(self, results: Dict) -> List[Dict]:
        """Get symbols with high dilution risk"""
        high_risk = []
        for symbol, data in results.items():
            if data.get('risk_level') in ['HIGH', 'CRITICAL']:
                high_risk.append({
                    'symbol': symbol,
                    'risk_score': data['risk_score'],
                    'flags': data['flags']
                })
        return sorted(high_risk, key=lambda x: x['risk_score'], reverse=True)
        
    def _get_recent_shelfs(self, results: Dict) -> List[Dict]:
        """Get symbols with recent shelf registrations"""
        shelfs = []
        for symbol, data in results.items():
            if data.get('shelf_active'):
                shelfs.append({
                    'symbol': symbol,
                    'amount': data.get('shelf_amount', 0),
                    'dilution_ratio': data.get('dilution_ratio', 0)
                })
        return sorted(shelfs, key=lambda x: x['dilution_ratio'], reverse=True)
        
    def _is_recent(self, date_str: str) -> bool:
        """Check if date is within lookback period"""
        try:
            filing_date = datetime.fromisoformat(date_str)
            cutoff = datetime.now() - timedelta(days=self.lookback_days)
            return filing_date > cutoff
        except:
            return False
            
    def _contains_dilution_keywords(self, text: str) -> bool:
        """Check if text contains dilution-related keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.dilution_keywords)
        
    def _extract_amount(self, text: str) -> float:
        """Extract dollar amount from filing text"""
        # Simple regex to find dollar amounts
        import re
        pattern = r'\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion)?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            # Convert to number
            amount_str = matches[0].replace(',', '')
            amount = float(amount_str)
            
            # Check for million/billion
            if 'million' in text.lower():
                amount *= 1e6
            elif 'billion' in text.lower():
                amount *= 1e9
                
            return amount
        return 0