#!/usr/bin/env python3
"""
BCD Reader
Reads BCD (Binary Coded Decimal) input from YAESU/KENWOOD radios
"""

import lgpio
import time
import logging
from typing import Dict, Optional, Tuple

class BCDReader:
    """Reads 4-bit BCD input from radio band data pins"""

    # Standard band codes (YAESU/KENWOOD)
    BAND_CODES = {
        0: "N/A",
        1: "160m",
        2: "80m",
        3: "60m",
        4: "40m",
        5: "30m",
        6: "20m",
        7: "17m",
        8: "15m",
        9: "12m",
        10: "10m",
        11: "6m",
        12: "4m",
        13: "2m",
        14: "70cm",
        15: "23cm"
    }

    def __init__(self, gpio_handle: int, pins: Dict[str, int], name: str = "Radio"):
        """
        Initialize BCD reader

        Args:
            gpio_handle: lgpio chip handle
            pins: Dictionary with keys 'D0', 'D1', 'D2', 'D3' (GPIO pin numbers)
            name: Radio name for logging
        """
        self.gpio_handle = gpio_handle
        self.pins = pins
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Validate pins
        required_pins = ['D0', 'D1', 'D2', 'D3']
        for pin_name in required_pins:
            if pin_name not in pins:
                raise ValueError(f"Missing pin definition: {pin_name}")

        # State tracking
        self.last_value = None
        self.last_band = None
        self.debounce_time = 0.02  # 20ms default
        self.last_change_time = 0

    def initialize(self) -> bool:
        """Configure BCD input pins"""
        try:
            self.logger.info(f"Initializing BCD reader for {self.name}...")

            # Configure all pins as inputs with pull-down
            for pin_name, pin_num in self.pins.items():
                lgpio.gpio_claim_input(self.gpio_handle, pin_num, lgpio.SET_PULL_DOWN)
                self.logger.debug(f"Configured {pin_name} (GPIO{pin_num}) as input")

            # Initial read
            self.last_value = self.read_raw()
            self.last_band = self.get_band_name(self.last_value)

            self.logger.info(f"BCD reader initialized: {self.name} → {self.last_band} (BCD={self.last_value})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize BCD reader: {e}")
            return False

    def read_raw(self) -> int:
        """
        Read raw BCD value (0-15)

        Returns:
            4-bit BCD value (0-15)
        """
        try:
            # Read each bit
            d0 = lgpio.gpio_read(self.gpio_handle, self.pins['D0'])
            d1 = lgpio.gpio_read(self.gpio_handle, self.pins['D1'])
            d2 = lgpio.gpio_read(self.gpio_handle, self.pins['D2'])
            d3 = lgpio.gpio_read(self.gpio_handle, self.pins['D3'])

            # Combine into 4-bit value
            value = d0 + (d1 << 1) + (d2 << 2) + (d3 << 3)

            return value

        except Exception as e:
            self.logger.error(f"Failed to read BCD: {e}")
            return 0

    def read_bits(self) -> Tuple[int, int, int, int]:
        """
        Read individual BCD bits

        Returns:
            Tuple of (D0, D1, D2, D3) values
        """
        try:
            d0 = lgpio.gpio_read(self.gpio_handle, self.pins['D0'])
            d1 = lgpio.gpio_read(self.gpio_handle, self.pins['D1'])
            d2 = lgpio.gpio_read(self.gpio_handle, self.pins['D2'])
            d3 = lgpio.gpio_read(self.gpio_handle, self.pins['D3'])
            return (d0, d1, d2, d3)
        except Exception as e:
            self.logger.error(f"Failed to read BCD bits: {e}")
            return (0, 0, 0, 0)

    def get_band_name(self, bcd_value: int) -> str:
        """
        Convert BCD value to band name

        Args:
            bcd_value: BCD code (0-15)

        Returns:
            Band name (e.g., "20m")
        """
        return self.BAND_CODES.get(bcd_value, "???")

    def read(self) -> Tuple[int, str]:
        """
        Read BCD value and band name

        Returns:
            Tuple of (bcd_value, band_name)
        """
        value = self.read_raw()
        band = self.get_band_name(value)
        return (value, band)

    def read_debounced(self) -> Optional[Tuple[int, str]]:
        """
        Read BCD with debouncing - only returns on stable changes

        Returns:
            Tuple of (bcd_value, band_name) if changed, None if no change
        """
        current_value = self.read_raw()
        current_time = time.time()

        # Check if value has changed
        if current_value != self.last_value:
            # Check debounce time
            if (current_time - self.last_change_time) >= self.debounce_time:
                # Stable change detected
                self.last_value = current_value
                self.last_band = self.get_band_name(current_value)
                self.last_change_time = current_time

                self.logger.info(f"{self.name} band changed → {self.last_band} (BCD={current_value})")
                return (current_value, self.last_band)
            else:
                # Still bouncing, ignore
                return None
        else:
            # No change
            return None

    def get_current_band(self) -> Tuple[int, str]:
        """
        Get last known band (no GPIO read)

        Returns:
            Tuple of (bcd_value, band_name)
        """
        return (self.last_value, self.last_band)

    def set_debounce_time(self, seconds: float):
        """Set debounce time in seconds"""
        self.debounce_time = seconds
        self.logger.debug(f"Debounce time set to {seconds*1000}ms")


if __name__ == "__main__":
    # Test code
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Radio 1 BCD pins
    radio1_pins = {
        'D0': 14,
        'D1': 15,
        'D2': 10,
        'D3': 9
    }

    # Open GPIO
    gpio_h = lgpio.gpiochip_open(0)

    try:
        reader = BCDReader(gpio_h, radio1_pins, "Radio1")

        if reader.initialize():
            print("\nMonitoring BCD input (Press CTRL+C to stop)...")
            print("-" * 60)

            while True:
                # Check for changes
                result = reader.read_debounced()

                if result:
                    bcd, band = result
                    bits = reader.read_bits()
                    print(f"[{time.strftime('%H:%M:%S')}] BCD={bcd:2d} ({bits[3]}{bits[2]}{bits[1]}{bits[0]}) → {band}")

                time.sleep(0.05)  # 50ms polling

    except KeyboardInterrupt:
        print("\n\nTest stopped by user")

    finally:
        lgpio.gpiochip_close(gpio_h)
