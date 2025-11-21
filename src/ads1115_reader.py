#!/usr/bin/env python3
"""
ADS1115 Reader
Reads voltage from ADS1115 ADC for ICOM radios band voltage detection
"""

import time
import logging
from typing import Optional, Tuple, List
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    ADS_AVAILABLE = True
except ImportError:
    ADS_AVAILABLE = False
    logging.warning("adafruit_ads1x15 library not available - ICOM support disabled")


class ADS1115Reader:
    """Reads voltage from ADS1115 for ICOM band detection"""

    def __init__(self, address: int = 0x48, channel: int = 0, name: str = "Radio"):
        """
        Initialize ADS1115 reader

        Args:
            address: I2C address (0x48, 0x49, 0x4A, 0x4B)
            channel: ADC channel (0-3)
            name: Radio name for logging
        """
        if not ADS_AVAILABLE:
            raise RuntimeError("adafruit_ads1x15 library not installed")

        self.address = address
        self.channel = channel
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        self.i2c = None
        self.ads = None
        self.chan = None

        # State tracking
        self.last_voltage = 0.0
        self.last_band = "N/A"
        self.debounce_time = 0.02  # 20ms default
        self.last_change_time = 0

        # Band voltage ranges (will be set from config)
        self.band_ranges = []

    def initialize(self) -> bool:
        """Initialize I2C and ADS1115"""
        try:
            self.logger.info(f"Initializing ADS1115 reader for {self.name} at 0x{self.address:02X}...")

            # Create I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)

            # Create ADS1115 object
            self.ads = ADS.ADS1115(self.i2c, address=self.address)

            # Set gain for 0-5V range (GAIN = 1 → ±4.096V)
            self.ads.gain = 1

            # Create analog input channel
            if self.channel == 0:
                self.chan = AnalogIn(self.ads, ADS.P0)
            elif self.channel == 1:
                self.chan = AnalogIn(self.ads, ADS.P1)
            elif self.channel == 2:
                self.chan = AnalogIn(self.ads, ADS.P2)
            elif self.channel == 3:
                self.chan = AnalogIn(self.ads, ADS.P3)
            else:
                raise ValueError(f"Invalid channel: {self.channel}")

            # Test read
            voltage = self.chan.voltage
            self.last_voltage = voltage

            self.logger.info(f"ADS1115 initialized: {self.name} channel {self.channel} → {voltage:.2f}V")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize ADS1115: {e}")
            return False

    def set_band_ranges(self, bands: List[dict]):
        """
        Set band voltage ranges from config

        Args:
            bands: List of band dicts with 'name' and 'icom_voltage' [min, max]
        """
        self.band_ranges = []
        for band in bands:
            if 'icom_voltage' in band:
                self.band_ranges.append({
                    'name': band['name'],
                    'min_v': band['icom_voltage'][0],
                    'max_v': band['icom_voltage'][1]
                })

        self.logger.info(f"Loaded {len(self.band_ranges)} band voltage ranges")

    def read_voltage(self) -> float:
        """
        Read voltage from ADC

        Returns:
            Voltage in volts
        """
        try:
            if self.chan is None:
                return 0.0

            voltage = self.chan.voltage
            return voltage

        except Exception as e:
            self.logger.error(f"Failed to read voltage: {e}")
            return 0.0

    def read_raw(self) -> int:
        """
        Read raw ADC value

        Returns:
            Raw 16-bit ADC value
        """
        try:
            if self.chan is None:
                return 0

            return self.chan.value

        except Exception as e:
            self.logger.error(f"Failed to read raw ADC: {e}")
            return 0

    def voltage_to_band(self, voltage: float) -> str:
        """
        Convert voltage to band name

        Args:
            voltage: Voltage reading

        Returns:
            Band name or "N/A"
        """
        for band_range in self.band_ranges:
            if band_range['min_v'] <= voltage <= band_range['max_v']:
                return band_range['name']

        return "N/A"

    def read(self) -> Tuple[float, str]:
        """
        Read voltage and band name

        Returns:
            Tuple of (voltage, band_name)
        """
        voltage = self.read_voltage()
        band = self.voltage_to_band(voltage)
        return (voltage, band)

    def read_debounced(self) -> Optional[Tuple[float, str]]:
        """
        Read voltage with debouncing - only returns on stable band changes

        Returns:
            Tuple of (voltage, band_name) if band changed, None if no change
        """
        voltage = self.read_voltage()
        band = self.voltage_to_band(voltage)
        current_time = time.time()

        # Check if band has changed
        if band != self.last_band:
            # Check debounce time
            if (current_time - self.last_change_time) >= self.debounce_time:
                # Stable change detected
                self.last_voltage = voltage
                self.last_band = band
                self.last_change_time = current_time

                self.logger.info(f"{self.name} band changed → {band} ({voltage:.2f}V)")
                return (voltage, band)
            else:
                # Still bouncing, ignore
                return None
        else:
            # Update voltage but band unchanged
            self.last_voltage = voltage
            return None

    def get_current_band(self) -> Tuple[float, str]:
        """
        Get last known band (no ADC read)

        Returns:
            Tuple of (voltage, band_name)
        """
        return (self.last_voltage, self.last_band)

    def set_debounce_time(self, seconds: float):
        """Set debounce time in seconds"""
        self.debounce_time = seconds
        self.logger.debug(f"Debounce time set to {seconds*1000}ms")


if __name__ == "__main__":
    # Test code
    if not ADS_AVAILABLE:
        print("ERROR: adafruit_ads1x15 library not installed")
        print("Install with: pip3 install adafruit-ads1x15")
        exit(1)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test band ranges (ICOM standard)
    test_bands = [
        {'name': '160m', 'icom_voltage': [0.0, 0.4]},
        {'name': '80m', 'icom_voltage': [0.4, 0.7]},
        {'name': '40m', 'icom_voltage': [0.8, 1.1]},
        {'name': '20m', 'icom_voltage': [1.8, 2.2]},
        {'name': '15m', 'icom_voltage': [2.8, 3.2]},
        {'name': '10m', 'icom_voltage': [3.8, 4.2]}
    ]

    try:
        reader = ADS1115Reader(address=0x48, channel=0, name="Radio1_ICOM")
        reader.set_band_ranges(test_bands)

        if reader.initialize():
            print("\nMonitoring voltage input (Press CTRL+C to stop)...")
            print("-" * 60)

            while True:
                # Check for changes
                result = reader.read_debounced()

                if result:
                    voltage, band = result
                    print(f"[{time.strftime('%H:%M:%S')}] {voltage:.2f}V → {band}")
                else:
                    # Show current voltage every second
                    voltage, band = reader.get_current_band()
                    print(f"[{time.strftime('%H:%M:%S')}] {voltage:.2f}V (no change)", end='\r')

                time.sleep(0.05)  # 50ms polling

    except KeyboardInterrupt:
        print("\n\nTest stopped by user")

    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nPossible issues:")
        print("  - ADS1115 not connected")
        print("  - Wrong I2C address (try 0x48, 0x49)")
        print("  - I2C not enabled (raspi-config)")
