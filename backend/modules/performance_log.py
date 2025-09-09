"""
Performance Logger Module
Writes standardized rows to CSV for auditing and analytics
"""
import csv
from datetime import datetime
from pathlib import Path


class PerformanceLogger:
    """Logs performance data to CSV"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.csv_path = Path(config.get('csv_output', 'data/performance.csv'))
        self.csv_path.parent.mkdir(exist_ok=True)
        self._init_csv()
        
    def _init_csv(self):
        """Initialize CSV with headers if needed"""
        if not self.csv_path.exists():
            headers = ['timestamp', 'symbol', 'tier', 'confidence', 'entry_price', 
                      'exit_price', 'pnl', 'duration', 'result']
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
    def log(self, row: Dict):
        """Log a performance row"""
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                row.get('timestamp', datetime.now().isoformat()),
                row.get('symbol'),
                row.get('tier'),
                row.get('confidence'),
                row.get('entry_price'),
                row.get('exit_price'),
                row.get('pnl'),
                row.get('duration'),
                row.get('result')
            ])