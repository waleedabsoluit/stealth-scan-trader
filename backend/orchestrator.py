"""
STEALTH Bot Orchestrator
Purpose: Main coordination layer that wires modules, executes scan ticks, 
aggregates outputs, handles logging, metrics, and alerts.
"""

import time
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.config_loader import load_config, is_module_enabled
from modules.obv_vwap_engine import OBVVWAPEngine
from modules.float_churn import FloatChurnAnalyzer
from modules.dilution_detector import DilutionDetector
from modules.orderbook_imbalance import OrderbookImbalanceTracker
from modules.squeeze_potential_scanner import SqueezePotentialScanner
from modules.pattern_scorer import PatternScorer
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.confidence_scorer import ConfidenceScorer
from modules.stealth_builder_tracker import StealthBuilderTracker
from modules.platinum_tier_gatekeeper import PlatinumTierGatekeeper
from modules.cooldown_registry import CooldownRegistry
from modules.confidence_calibrator import ConfidenceCalibrator
from modules.fallback_handler import FallbackHandler
from modules.market_scanner import MarketScanner
from modules.performance_log import PerformanceLogger
from infra.metrics import (
    REQUEST_COUNT, REQUEST_LATENCY, SIGNALS_BY_TIER, 
    REJECT_COUNT, orchestrator_metrics
)
from infra.logging_setup import setup_json_logging


class StealthBotOrchestrator:
    """Main orchestrator for the STEALTH Bot system."""
    
    def __init__(self, config_path: str = 'config/config.yml'):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.logger = self._setup_logging()
        self.modules = {}
        self.cooldown_registry = CooldownRegistry()
        self.performance_logger = PerformanceLogger()
        self.calibrator = ConfidenceCalibrator()
        self.fallback_handler = FallbackHandler()
        
        # Initialize modules
        self._initialize_modules()
        
        self.logger.info("STEALTH Bot Orchestrator initialized", 
                        extra={"modules": list(self.modules.keys())})
    
    def _setup_logging(self) -> logging.Logger:
        """Setup JSON logging for the orchestrator."""
        log_config = self.config.get('logging', {})
        setup_json_logging(level=log_config.get('level', 'INFO'))
        return logging.getLogger(__name__)
    
    def _initialize_modules(self):
        """Initialize all enabled modules based on configuration."""
        module_classes = {
            'obv_vwap': OBVVWAPEngine,
            'float_churn': FloatChurnAnalyzer,
            'dilution_detector': DilutionDetector,
            'orderbook_imbalance': OrderbookImbalanceTracker,
            'squeeze_potential': SqueezePotentialScanner,
            'pattern_scorer': PatternScorer,
            'sentiment_analyzer': SentimentAnalyzer,
            'confidence_scorer': ConfidenceScorer,
            'stealth_builder': StealthBuilderTracker,
            'platinum_gatekeeper': PlatinumTierGatekeeper,
            'market_scanner': MarketScanner,
        }
        
        for module_name, module_class in module_classes.items():
            if is_module_enabled(self.config, module_name):
                try:
                    module_config = self.config['modules'].get(module_name, {})
                    self.modules[module_name] = module_class(module_config)
                    self.logger.info(f"Initialized module: {module_name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize module {module_name}: {e}")
    
    def _auto_wired_modules(self, universe_provider: Any) -> Dict[str, Any]:
        """
        Auto-wire modules with universe provider.
        
        Args:
            universe_provider: Provider for market universe data
            
        Returns:
            Dictionary of wired modules
        """
        wired = {}
        for name, module in self.modules.items():
            try:
                if hasattr(module, 'set_universe'):
                    module.set_universe(universe_provider)
                wired[name] = module
            except Exception as e:
                self.logger.error(f"Failed to wire module {name}: {e}")
                wired[name] = self.fallback_handler
        
        return wired
    
    @orchestrator_metrics
    def run_autowired_tick(self, context: Dict, universe_provider: Any) -> Dict[str, Any]:
        """
        Execute one scan tick with all wired modules.
        
        Args:
            context: Execution context with market data
            universe_provider: Provider for market universe
            
        Returns:
            Aggregated results from all modules
        """
        start_time = time.time()
        REQUEST_COUNT.inc()
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'context': context,
            'signals': [],
            'metrics': {},
            'errors': [],
        }
        
        try:
            # Wire modules
            wired_modules = self._auto_wired_modules(universe_provider)
            
            # Get market data
            market_data = self._get_market_data(context, universe_provider)
            
            # Execute modules in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {}
                
                for module_name, module in wired_modules.items():
                    if module_name in ['confidence_scorer', 'platinum_gatekeeper']:
                        continue  # These run after other modules
                    
                    future = executor.submit(self._execute_module, 
                                           module_name, module, market_data)
                    futures[future] = module_name
                
                # Collect results
                module_outputs = {}
                for future in as_completed(futures):
                    module_name = futures[future]
                    try:
                        output = future.result(timeout=5)
                        module_outputs[module_name] = output
                    except Exception as e:
                        self.logger.error(f"Module {module_name} failed: {e}")
                        results['errors'].append({
                            'module': module_name,
                            'error': str(e),
                            'traceback': traceback.format_exc()
                        })
            
            # Aggregate signals
            signals = self._aggregate_signals(module_outputs, wired_modules)
            
            # Apply confidence scoring
            if 'confidence_scorer' in wired_modules:
                signals = self._apply_confidence_scoring(signals, wired_modules['confidence_scorer'])
            
            # Apply platinum gatekeeper
            if 'platinum_gatekeeper' in wired_modules:
                signals = self._apply_gatekeeper(signals, wired_modules['platinum_gatekeeper'])
            
            # Filter cooldowns
            signals = self._filter_cooldowns(signals)
            
            # Calibrate confidence
            signals = self._calibrate_confidence(signals)
            
            # Log performance
            self._log_performance(signals)
            
            # Update metrics
            self._update_metrics(signals)
            
            results['signals'] = signals
            results['metrics'] = self._collect_metrics()
            
        except Exception as e:
            self.logger.error(f"Orchestrator tick failed: {e}", 
                            extra={'traceback': traceback.format_exc()})
            results['errors'].append({
                'module': 'orchestrator',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        
        finally:
            # Record latency
            latency = time.time() - start_time
            REQUEST_LATENCY.observe(latency)
            results['latency'] = latency
        
        return results
    
    def _execute_module(self, name: str, module: Any, data: Dict) -> Dict:
        """
        Execute a single module with error handling.
        
        Args:
            name: Module name
            module: Module instance
            data: Market data
            
        Returns:
            Module output or fallback result
        """
        try:
            if hasattr(module, 'analyze'):
                return module.analyze(data)
            elif hasattr(module, 'scan'):
                return module.scan(data)
            elif hasattr(module, 'compute'):
                return module.compute(data)
            else:
                self.logger.warning(f"Module {name} has no execution method")
                return {}
        except Exception as e:
            self.logger.error(f"Module {name} execution failed: {e}")
            return self.fallback_handler.get_default(name)
    
    def _get_market_data(self, context: Dict, universe_provider: Any) -> Dict:
        """
        Retrieve market data from universe provider.
        
        Args:
            context: Execution context
            universe_provider: Market data provider
            
        Returns:
            Market data dictionary
        """
        try:
            if hasattr(universe_provider, 'get_universe'):
                symbols = universe_provider.get_universe(context)
            else:
                symbols = []
            
            return {
                'symbols': symbols,
                'timestamp': datetime.utcnow(),
                'session': context.get('session', 'regular'),
                'context': context,
            }
        except Exception as e:
            self.logger.error(f"Failed to get market data: {e}")
            return {
                'symbols': [],
                'timestamp': datetime.utcnow(),
                'session': 'unknown',
                'context': context,
            }
    
    def _aggregate_signals(self, outputs: Dict, modules: Dict) -> List[Dict]:
        """
        Aggregate signals from all module outputs.
        
        Args:
            outputs: Module outputs
            modules: Module instances
            
        Returns:
            List of aggregated signals
        """
        signals = []
        signal_map = {}
        
        for module_name, output in outputs.items():
            if not output or 'signals' not in output:
                continue
            
            for signal in output['signals']:
                symbol = signal.get('symbol')
                if not symbol:
                    continue
                
                if symbol not in signal_map:
                    signal_map[symbol] = {
                        'symbol': symbol,
                        'modules': {},
                        'scores': [],
                        'timestamp': datetime.utcnow().isoformat(),
                    }
                
                signal_map[symbol]['modules'][module_name] = signal
                
                if 'score' in signal:
                    signal_map[symbol]['scores'].append(signal['score'])
        
        # Convert to list
        for symbol, data in signal_map.items():
            if data['scores']:
                data['aggregate_score'] = sum(data['scores']) / len(data['scores'])
            else:
                data['aggregate_score'] = 0
            
            signals.append(data)
        
        # Sort by aggregate score
        signals.sort(key=lambda x: x.get('aggregate_score', 0), reverse=True)
        
        return signals
    
    def _apply_confidence_scoring(self, signals: List[Dict], scorer: Any) -> List[Dict]:
        """Apply confidence scoring to signals."""
        try:
            for signal in signals:
                confidence = scorer.score(signal)
                signal['confidence'] = confidence
                signal['tier'] = self._determine_tier(confidence)
        except Exception as e:
            self.logger.error(f"Confidence scoring failed: {e}")
        
        return signals
    
    def _determine_tier(self, confidence: float) -> str:
        """Determine signal tier based on confidence."""
        if confidence >= 90:
            return 'PLATINUM'
        elif confidence >= 75:
            return 'GOLD'
        elif confidence >= 60:
            return 'SILVER'
        else:
            return 'BRONZE'
    
    def _apply_gatekeeper(self, signals: List[Dict], gatekeeper: Any) -> List[Dict]:
        """Apply platinum tier gatekeeper filtering."""
        filtered = []
        
        for signal in signals:
            if signal.get('tier') == 'PLATINUM':
                if gatekeeper.validate(signal):
                    filtered.append(signal)
                else:
                    REJECT_COUNT.labels(reason='gatekeeper').inc()
                    signal['tier'] = 'GOLD'  # Downgrade
                    filtered.append(signal)
            else:
                filtered.append(signal)
        
        return filtered
    
    def _filter_cooldowns(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals based on cooldown registry."""
        filtered = []
        
        for signal in signals:
            symbol = signal.get('symbol')
            if symbol and not self.cooldown_registry.is_active(symbol):
                filtered.append(signal)
                
                # Add to cooldown if high tier
                if signal.get('tier') in ['PLATINUM', 'GOLD']:
                    self.cooldown_registry.set_cooldown(
                        symbol, 
                        minutes=30,
                        reason=f"Signal generated: {signal.get('tier')}"
                    )
            else:
                REJECT_COUNT.labels(reason='cooldown').inc()
        
        return filtered
    
    def _calibrate_confidence(self, signals: List[Dict]) -> List[Dict]:
        """Calibrate confidence scores based on historical performance."""
        try:
            for signal in signals:
                if 'confidence' in signal:
                    calibrated = self.calibrator.calibrate(
                        signal['confidence'],
                        signal.get('tier', 'BRONZE')
                    )
                    signal['confidence_raw'] = signal['confidence']
                    signal['confidence'] = calibrated
        except Exception as e:
            self.logger.error(f"Confidence calibration failed: {e}")
        
        return signals
    
    def _log_performance(self, signals: List[Dict]):
        """Log performance metrics for signals."""
        for signal in signals:
            try:
                self.performance_logger.log({
                    'timestamp': signal.get('timestamp'),
                    'symbol': signal.get('symbol'),
                    'tier': signal.get('tier'),
                    'confidence': signal.get('confidence'),
                    'aggregate_score': signal.get('aggregate_score'),
                    'modules': list(signal.get('modules', {}).keys()),
                })
            except Exception as e:
                self.logger.error(f"Performance logging failed: {e}")
    
    def _update_metrics(self, signals: List[Dict]):
        """Update Prometheus metrics."""
        tier_counts = {}
        for signal in signals:
            tier = signal.get('tier', 'UNKNOWN')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        for tier, count in tier_counts.items():
            SIGNALS_BY_TIER.labels(tier=tier).inc(count)
    
    def _collect_metrics(self) -> Dict:
        """Collect current metrics snapshot."""
        return {
            'total_signals': len(self.modules),
            'active_modules': sum(1 for m in self.modules.values() if m),
            'cooldowns_active': self.cooldown_registry.active_count(),
            'timestamp': datetime.utcnow().isoformat(),
        }


# Main entry point
if __name__ == "__main__":
    orchestrator = StealthBotOrchestrator()
    
    # Example tick execution
    context = {
        'session': 'regular',
        'force_scan': False,
    }
    
    # Mock universe provider
    class MockUniverseProvider:
        def get_universe(self, context):
            return ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'TSLA']
    
    provider = MockUniverseProvider()
    results = orchestrator.run_autowired_tick(context, provider)
    
    print(f"Scan completed: {len(results['signals'])} signals generated")
    print(f"Latency: {results['latency']:.2f}s")