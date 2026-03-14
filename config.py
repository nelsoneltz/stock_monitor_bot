import json
from typing import Dict

class Config:
    """Configuration manager for stock monitoring thresholds."""
    
    def __init__(self, config_file: str = 'stock_thresholds.json'):
        self.config_file = config_file
        self.thresholds = self._load_config()
    
    def _load_config(self) -> Dict[str, float]:
        """Load stock thresholds from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config if file doesn't exist
            default_config = {
                "AURA33": 130.0,
                "PETR4": 29.0,
                "VALE3": 70.0
            }
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, float]) -> None:
        """Save stock thresholds to JSON file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def get_threshold(self, ticker: str) -> float:
        """Get the minimum threshold value for a ticker."""
        return self.thresholds.get(ticker, 0.0)
    
    def set_threshold(self, ticker: str, value: float) -> None:
        """Set the minimum threshold value for a ticker."""
        self.thresholds[ticker] = value
        self._save_config(self.thresholds)
    
    def remove_threshold(self, ticker: str) -> None:
        """Remove a ticker from thresholds."""
        if ticker in self.thresholds:
            del self.thresholds[ticker]
            self._save_config(self.thresholds)