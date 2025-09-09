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
        
    def set_cooldown(self, symbol: str, minutes: int, reason: str):
        """Set cooldown for a symbol"""
        expiry = datetime.now() + timedelta(minutes=minutes)
        self.cooldowns[symbol] = {
            'expiry': expiry,
            'reason': reason,
            'minutes': minutes
        }
        
    def is_active(self, symbol: str) -> bool:
        """Check if symbol is in cooldown"""
        if symbol not in self.cooldowns:
            return False
            
        cooldown = self.cooldowns[symbol]
        if datetime.now() >= cooldown['expiry']:
            del self.cooldowns[symbol]
            return False
            
        return True
        
    def active_count(self) -> int:
        """Get count of active cooldowns"""
        # Clean expired cooldowns
        now = datetime.now()
        expired = [s for s, c in self.cooldowns.items() if now >= c['expiry']]
        for symbol in expired:
            del self.cooldowns[symbol]
        return len(self.cooldowns)
        
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