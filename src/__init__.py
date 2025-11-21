"""
Dual Band Decoder Package
Ham Radio Station Controller for SO2R operation
"""

__version__ = "1.0.0"
__author__ = "IZ7KHR"

from .config_loader import ConfigLoader
from .gpio_controller import GPIOController
from .bcd_reader import BCDReader

try:
    from .ads1115_reader import ADS1115Reader
    __all__ = ['ConfigLoader', 'GPIOController', 'BCDReader', 'ADS1115Reader']
except ImportError:
    __all__ = ['ConfigLoader', 'GPIOController', 'BCDReader']
