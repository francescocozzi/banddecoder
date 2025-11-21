#!/usr/bin/env python3
"""
Band Decoder - Main Application
Automatic band decoder for dual radio SO2R operation
"""

import lgpio
import time
import signal
import sys
import logging
from typing import Optional, Dict
from pathlib import Path

# Import local modules
from config_loader import ConfigLoader
from gpio_controller import GPIOController
from bcd_reader import BCDReader
try:
    from ads1115_reader import ADS1115Reader
    ADS_AVAILABLE = True
except ImportError:
    ADS_AVAILABLE = False


class BandDecoder:
    """Main band decoder controller"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize band decoder

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = None
        self.gpio_handle = None
        self.running = False

        # Controllers
        self.relay_board1 = None
        self.relay_board2 = None
        self.radio1_bcd = None
        self.radio2_bcd = None
        self.radio1_icom = None
        self.radio2_icom = None

        # State tracking
        self.radio1_band = "N/A"
        self.radio2_band = "N/A"
        self.radio1_type = "bcd"  # "bcd" or "icom"
        self.radio2_type = "bcd"

        # Setup logging
        self.logger = None
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging"""
        log_level = logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)

    def load_config(self) -> bool:
        """Load configuration from YAML"""
        try:
            self.logger.info(f"Loading configuration from {self.config_path}...")
            self.config = ConfigLoader(self.config_path)

            # Update logging level
            log_level = self.config.get('system.log_level', 'INFO')
            logging.getLogger().setLevel(getattr(logging, log_level))

            self.logger.info("Configuration loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False

    def initialize_gpio(self) -> bool:
        """Initialize GPIO chip"""
        try:
            self.logger.info("Initializing GPIO chip...")
            self.gpio_handle = lgpio.gpiochip_open(0)
            self.logger.info(f"GPIO chip opened: handle={self.gpio_handle}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            return False

    def initialize_relays(self) -> bool:
        """Initialize relay boards"""
        try:
            self.logger.info("Initializing relay boards...")

            # Relay Board 1 (Radio 1 filters)
            board1_pins = self.config.get('relays.board1.pins')
            board1_logic = self.config.get('relays.board1.logic')
            self.relay_board1 = GPIOController(board1_pins, logic=board1_logic)
            if not self.relay_board1.initialize():
                return False

            # Relay Board 2 (Radio 2 filters + antenna switch)
            board2_pins = self.config.get('relays.board2.pins')
            board2_logic = self.config.get('relays.board2.logic')
            self.relay_board2 = GPIOController(board2_pins, logic=board2_logic)
            if not self.relay_board2.initialize():
                return False

            self.logger.info("Relay boards initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize relays: {e}")
            return False

    def initialize_radios(self) -> bool:
        """Initialize radio input readers"""
        try:
            self.logger.info("Initializing radio readers...")

            # Radio 1
            radio1_type = self.config.get('radios.radio1.type', 'auto')
            radio1_bcd_pins = {
                'D0': self.config.get('radios.radio1.bcd_pins.d0'),
                'D1': self.config.get('radios.radio1.bcd_pins.d1'),
                'D2': self.config.get('radios.radio1.bcd_pins.d2'),
                'D3': self.config.get('radios.radio1.bcd_pins.d3')
            }

            # Initialize BCD reader for Radio 1
            self.radio1_bcd = BCDReader(self.gpio_handle, radio1_bcd_pins, "Radio1")
            if not self.radio1_bcd.initialize():
                return False

            # Radio 2
            radio2_bcd_pins = {
                'D0': self.config.get('radios.radio2.bcd_pins.d0'),
                'D1': self.config.get('radios.radio2.bcd_pins.d1'),
                'D2': self.config.get('radios.radio2.bcd_pins.d2'),
                'D3': self.config.get('radios.radio2.bcd_pins.d3')
            }

            self.radio2_bcd = BCDReader(self.gpio_handle, radio2_bcd_pins, "Radio2")
            if not self.radio2_bcd.initialize():
                return False

            # Initialize ICOM readers if enabled
            if ADS_AVAILABLE and self.config.get('radios.radio1.icom.enabled'):
                self.logger.info("Initializing ICOM support for Radio 1...")
                try:
                    addr = self.config.get('radios.radio1.icom.ads1115_address')
                    self.radio1_icom = ADS1115Reader(address=addr, channel=0, name="Radio1_ICOM")
                    self.radio1_icom.set_band_ranges(self.config.get('bands'))
                    if self.radio1_icom.initialize():
                        self.radio1_type = "auto"  # Will auto-detect
                except Exception as e:
                    self.logger.warning(f"Failed to init ICOM Radio1: {e}")

            if ADS_AVAILABLE and self.config.get('radios.radio2.icom.enabled'):
                self.logger.info("Initializing ICOM support for Radio 2...")
                try:
                    addr = self.config.get('radios.radio2.icom.ads1115_address')
                    self.radio2_icom = ADS1115Reader(address=addr, channel=0, name="Radio2_ICOM")
                    self.radio2_icom.set_band_ranges(self.config.get('bands'))
                    if self.radio2_icom.initialize():
                        self.radio2_type = "auto"
                except Exception as e:
                    self.logger.warning(f"Failed to init ICOM Radio2: {e}")

            self.logger.info("Radio readers initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize radios: {e}")
            return False

    def get_band_relay_index(self, band_name: str, radio_num: int) -> Optional[int]:
        """
        Get relay index for a band

        Args:
            band_name: Band name (e.g., "20m")
            radio_num: 1 or 2

        Returns:
            Relay index or None
        """
        bands = self.config.get('bands')
        for band in bands:
            if band['name'] == band_name:
                if radio_num == 1:
                    return band.get('relay_radio1')
                elif radio_num == 2:
                    return band.get('relay_radio2')
        return None

    def switch_band(self, radio_num: int, band_name: str):
        """
        Switch relay for band change

        Args:
            radio_num: 1 or 2
            band_name: New band name
        """
        try:
            relay_index = self.get_band_relay_index(band_name, radio_num)

            if relay_index is None:
                self.logger.warning(f"No relay mapping for Radio{radio_num} band {band_name}")
                return

            # Get relay board
            relay_board = self.relay_board1 if radio_num == 1 else self.relay_board2

            # Turn off all relays for this radio first
            num_bands = len(self.config.get('bands'))
            for i in range(num_bands):
                relay_board.set_relay(i, False)

            # Turn on relay for new band
            relay_delay = self.config.get('timing.relay_delay', 0.01)
            relay_board.set_relay(relay_index, True, delay=relay_delay)

            self.logger.info(f"Radio{radio_num} switched to {band_name} (relay {relay_index})")

        except Exception as e:
            self.logger.error(f"Failed to switch band: {e}")

    def poll_radios(self):
        """Poll radio inputs and update relays"""
        try:
            # Poll Radio 1
            if self.radio1_type == "bcd":
                result = self.radio1_bcd.read_debounced()
                if result:
                    _, band = result
                    if band != self.radio1_band and band != "N/A":
                        self.radio1_band = band
                        self.switch_band(1, band)

            elif self.radio1_type == "icom" and self.radio1_icom:
                result = self.radio1_icom.read_debounced()
                if result:
                    _, band = result
                    if band != self.radio1_band and band != "N/A":
                        self.radio1_band = band
                        self.switch_band(1, band)

            # Poll Radio 2
            if self.radio2_type == "bcd":
                result = self.radio2_bcd.read_debounced()
                if result:
                    _, band = result
                    if band != self.radio2_band and band != "N/A":
                        self.radio2_band = band
                        self.switch_band(2, band)

            elif self.radio2_type == "icom" and self.radio2_icom:
                result = self.radio2_icom.read_debounced()
                if result:
                    _, band = result
                    if band != self.radio2_band and band != "N/A":
                        self.radio2_band = band
                        self.switch_band(2, band)

        except Exception as e:
            self.logger.error(f"Error polling radios: {e}")

    def run(self):
        """Main run loop"""
        try:
            self.running = True
            polling_interval = self.config.get('timing.polling_interval', 0.05)

            self.logger.info("=" * 70)
            self.logger.info("BAND DECODER RUNNING")
            self.logger.info("=" * 70)
            self.logger.info(f"Polling interval: {polling_interval*1000}ms")
            self.logger.info("Press CTRL+C to stop")
            self.logger.info("")

            while self.running:
                self.poll_radios()
                time.sleep(polling_interval)

        except KeyboardInterrupt:
            self.logger.info("\nShutdown requested by user")
            self.running = False

        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}")
            self.running = False

    def cleanup(self):
        """Clean up resources"""
        try:
            self.logger.info("Cleaning up resources...")

            # Turn off all relays
            if self.relay_board1:
                self.relay_board1.cleanup()
            if self.relay_board2:
                self.relay_board2.cleanup()

            # Close GPIO
            if self.gpio_handle is not None:
                lgpio.gpiochip_close(self.gpio_handle)

            self.logger.info("Cleanup complete")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def signal_handler(sig, frame):
    """Handle SIGINT and SIGTERM"""
    print("\nSignal received, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 70)
    print("DUAL BAND DECODER - Ham Radio Station Controller")
    print("IO7T - IZ7KHR")
    print("=" * 70)
    print()

    # Create decoder instance
    decoder = BandDecoder()

    try:
        # Initialize
        if not decoder.load_config():
            print("ERROR: Failed to load configuration")
            return 1

        if not decoder.initialize_gpio():
            print("ERROR: Failed to initialize GPIO")
            return 1

        if not decoder.initialize_relays():
            print("ERROR: Failed to initialize relays")
            return 1

        if not decoder.initialize_radios():
            print("ERROR: Failed to initialize radios")
            return 1

        # Run main loop
        decoder.run()

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        return 1

    finally:
        decoder.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
