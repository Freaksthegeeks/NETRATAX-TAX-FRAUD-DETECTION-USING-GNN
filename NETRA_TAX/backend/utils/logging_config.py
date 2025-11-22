"""
Logging configuration
"""

import logging
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "netra_tax.log"),
            logging.StreamHandler()
        ]
    )

