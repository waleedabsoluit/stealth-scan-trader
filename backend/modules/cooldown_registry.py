"""
Cooldown Registry Module
Blocks repeated entries on the same symbol for a period
"""
from typing import Dict, Optional
from datetime import datetime, timedelta


class CooldownRegistry:
    """Manages cooldown periods for symbols"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.default_minutes = config.get('default_minutes', 30)
        self.cooldowns = {}
        
    def set(self, symbol: str, minutes: int, reason: str):
        """Set cooldown for a symbol"""
        expiry = datetime.now() + timedelta(minutes=minutes)
        self.cooldowns[symbol] = {
            'expiry': expiry,
            'reason': reason,
            'minutes': minutes
        }
        
    def active(self, symbol: str) -> Optional[Dict]:
        """Check if symbol is in cooldown"""
        if symbol not in self.cooldowns:
            return None
            
        cooldown = self.cooldowns[symbol]
        if datetime.now() >= cooldown['expiry']:
            del self.cooldowns[symbol]
            return None
            
        return cooldown
        
    def clear(self, symbol: str):
        """Clear cooldown for a symbol"""
        if symbol in self.cooldowns:
            del self.cooldowns[symbol]