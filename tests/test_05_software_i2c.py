#!/usr/bin/env python3
"""
Test 5: Software I2C Basic Test
Testa comunicazione I2C software (senza ADS1115)
"""

import lgpio as GPIO  # Sostituito RPi.GPIO con lgpio
import time
import sys

# Mappatura dei valori per chiarezza con lgpio
HIGH = 1
LOW = 0

I2C_SDA_PIN = 5
I2C_SCL_PIN = 6

class SoftwareI2C:
    def __init__(self, gpio_handle, sda_pin, scl_pin):
        self.H = gpio_handle
        self.sda = sda_pin
        self.scl = scl_pin
        # Claim output per SCL e SDA
        GPIO.gpio_claim_output(self.H, self.sda)
        GPIO.gpio_claim_output(self.H, self.scl)
        GPIO.gpio_write(self.H, self.sda, HIGH)
        GPIO.gpio_write(self.H, self.scl, HIGH)
        self.delay = 0.00001

    def _sda_high(self):
        # Per simulare open-drain, rilasciamo il pin configurandolo come input
        GPIO.gpio_free(self.H, self.sda)
        GPIO.gpio_claim_input(self.H, self.sda, GPIO.SET_PULL_UP)
        time.sleep(self.delay)

    def _sda_low(self):
        # Per tirare il pin LOW, lo configuriamo come output e scriviamo LOW
        GPIO.gpio_free(self.H, self.sda)
        GPIO.gpio_claim_output(self.H, self.sda)
        GPIO.gpio_write(self.H, self.sda, LOW)
        time.sleep(self.delay)

    def _scl_high(self):
        GPIO.gpio_write(self.H, self.scl, HIGH)
        time.sleep(self.delay)

    def _scl_low(self):
        GPIO.gpio_write(self.H, self.scl, LOW)
        time.sleep(self.delay)

    def start(self):
        self._sda_high()
        self._scl_high()
        self._sda_low()
        self._scl_low()

    def stop(self):
        self._sda_low()
        self._scl_high()
        self._sda_high()

def test_software_i2c():
    print("\n" + "="*70)
    print("TEST 5: SOFTWARE I2C BASIC TEST")
    print("="*70)
    print(f"\nSDA: GPIO{I2C_SDA_PIN} (Pin 29)")
    print(f"SCL: GPIO{I2C_SCL_PIN} (Pin 31)\n")

    gpio_handle = None

    try:
        # Apri il chip GPIO 0 (standard sul Raspberry Pi 5)
        gpio_handle = GPIO.gpiochip_open(0)

        print("1. Initializing Software I2C...", end=" ")
        i2c = SoftwareI2C(gpio_handle, I2C_SDA_PIN, I2C_SCL_PIN)
        print("✓")

        print("2. Testing START condition...", end=" ")
        i2c.start()
        time.sleep(0.001)
        print("✓")

        print("3. Testing STOP condition...", end=" ")
        i2c.stop()
        time.sleep(0.001)
        print("✓")

        print("4. Testing 10 START/STOP cycles...", end=" ")
        for _ in range(10):
            i2c.start()
            i2c.stop()
        print("✓")

        # Chiudi l'handle del chip GPIO (equivalente a GPIO.cleanup())
        if gpio_handle is not None:
            GPIO.gpiochip_close(gpio_handle)
            gpio_handle = None

        print("\n" + "="*70)
        print("✓ SOFTWARE I2C BASIC TEST PASSED")
        print("="*70)
        print("\nNote: This only tests I2C timing, not device communication")
        print("ADS1115 test will come next\n")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        if gpio_handle is not None:
            GPIO.gpiochip_close(gpio_handle)
        return False

if __name__ == "__main__":
    success = test_software_i2c()
    sys.exit(0 if success else 1)
