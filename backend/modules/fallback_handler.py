"""
Fallback Handler Module
Provides default responses when modules fail
"""
from typing import Dict, Any


class FallbackHandler:
    """Handles fallback scenarios"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
    def get_default(self, module_name: str) -> Dict[str, Any]:
        """
        Get default response for a failed module
        
        Args:
            module_name: Name of the failed module
            
        Returns:
            Default response dictionary
        """
        return {
            'signals': [],
            'metrics': {
                'status': 'fallback',
                'module': module_name,
                'error': 'Module execution failed'
            }
        }
        
    def analyze(self, market_data: Dict) -> Dict:
        """Fallback analyze method"""
        return self.get_default('unknown')