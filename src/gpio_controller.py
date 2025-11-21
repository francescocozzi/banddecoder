#!/usr/bin/env python3
"""
GPIO Controller
Manages GPIO pins and relay outputs for band decoder
"""

import lgpio
import time
import logging
from typing import List, Optional

class GPIOController:
    """Controls GPIO pins and relay boards"""

    def __init__(self, relay_pins: List[int], logic: str = "inverse"):
        """
        Initialize GPIO controller

        Args:
            relay_pins: List of GPIO pin numbers for relays
            logic: "inverse" (LOW=ON, HIGH=OFF) or "normal" (HIGH=ON, LOW=OFF)
        """
        self.relay_pins = relay_pins
        self.logic = logic
        self.gpio_handle = None
        self.logger = logging.getLogger(__name__)

        # Define logic values
        if logic == "inverse":
            self.ON = 0   # LOW
            self.OFF = 1  # HIGH
        else:
            self.ON = 1   # HIGH
            self.OFF = 0  # LOW

    def initialize(self) -> bool:
        """Initialize GPIO chip and configure relay pins"""
        try:
            self.logger.info("Initializing GPIO controller...")

            # Open GPIO chip 0 (standard on Raspberry Pi 5)
            self.gpio_handle = lgpio.gpiochip_open(0)
            self.logger.debug(f"GPIO chip opened: handle={self.gpio_handle}")

            # Configure all relay pins as outputs (default OFF)
            for pin in self.relay_pins:
                lgpio.gpio_claim_output(self.gpio_handle, pin)
                lgpio.gpio_write(self.gpio_handle, pin, self.OFF)
                self.logger.debug(f"Configured GPIO{pin} as output (OFF)")

            self.logger.info(f"GPIO controller initialized: {len(self.relay_pins)} relays")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            return False

    def set_relay(self, relay_index: int, state: bool, delay: float = 0.0) -> bool:
        """
        Set relay state

        Args:
            relay_index: Index in relay_pins list (0-based)
            state: True=ON, False=OFF
            delay: Optional delay after switching (seconds)

        Returns:
            True if successful
        """
        try:
            if relay_index < 0 or relay_index >= len(self.relay_pins):
                self.logger.error(f"Invalid relay index: {relay_index}")
                return False

            pin = self.relay_pins[relay_index]
            value = self.ON if state else self.OFF

            lgpio.gpio_write(self.gpio_handle, pin, value)

            state_str = "ON" if state else "OFF"
            self.logger.debug(f"Relay {relay_index} (GPIO{pin}) → {state_str}")

            if delay > 0:
                time.sleep(delay)

            return True

        except Exception as e:
            self.logger.error(f"Failed to set relay {relay_index}: {e}")
            return False

    def set_relay_by_pin(self, pin: int, state: bool, delay: float = 0.0) -> bool:
        """
        Set relay state by GPIO pin number

        Args:
            pin: GPIO pin number
            state: True=ON, False=OFF
            delay: Optional delay after switching (seconds)

        Returns:
            True if successful
        """
        try:
            if pin not in self.relay_pins:
                self.logger.error(f"GPIO{pin} not in configured relay pins")
                return False

            relay_index = self.relay_pins.index(pin)
            return self.set_relay(relay_index, state, delay)

        except Exception as e:
            self.logger.error(f"Failed to set relay GPIO{pin}: {e}")
            return False

    def all_off(self, delay: float = 0.0) -> bool:
        """Turn all relays OFF"""
        try:
            self.logger.info("Turning all relays OFF")
            for i in range(len(self.relay_pins)):
                self.set_relay(i, False, delay)
            return True
        except Exception as e:
            self.logger.error(f"Failed to turn all relays off: {e}")
            return False

    def all_on(self, delay: float = 0.0) -> bool:
        """Turn all relays ON (for testing)"""
        try:
            self.logger.info("Turning all relays ON")
            for i in range(len(self.relay_pins)):
                self.set_relay(i, True, delay)
            return True
        except Exception as e:
            self.logger.error(f"Failed to turn all relays on: {e}")
            return False

    def get_state(self, relay_index: int) -> Optional[bool]:
        """
        Get current relay state

        Args:
            relay_index: Index in relay_pins list (0-based)

        Returns:
            True=ON, False=OFF, None if error
        """
        try:
            if relay_index < 0 or relay_index >= len(self.relay_pins):
                return None

            pin = self.relay_pins[relay_index]
            value = lgpio.gpio_read(self.gpio_handle, pin)

            # Convert to logical state based on logic type
            return value == self.ON

        except Exception as e:
            self.logger.error(f"Failed to read relay {relay_index} state: {e}")
            return None

    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            if self.gpio_handle is not None:
                self.logger.info("Cleaning up GPIO controller...")

                # Turn all relays off before cleanup
                self.all_off()

                # Close GPIO chip
                lgpio.gpiochip_close(self.gpio_handle)
                self.gpio_handle = None

                self.logger.info("GPIO controller cleaned up")
        except Exception as e:
            self.logger.error(f"Error during GPIO cleanup: {e}")

    def __del__(self):
        """Destructor - ensure cleanup"""
        self.cleanup()


if __name__ == "__main__":
    # Test code
    logging.basicConfig(level=logging.DEBUG)

    # Test with first relay board pins
    test_pins = [18, 23, 24, 25, 8, 7, 12, 16]

    controller = GPIOController(test_pins, logic="inverse")

    if controller.initialize():
        print("Testing relay sequence...")

        # Test each relay
        for i in range(len(test_pins)):
            print(f"\nRelay {i} ON")
            controller.set_relay(i, True)
            time.sleep(0.5)

            print(f"Relay {i} OFF")
            controller.set_relay(i, False)
            time.sleep(0.5)

        print("\nTest complete")
        controller.cleanup()
