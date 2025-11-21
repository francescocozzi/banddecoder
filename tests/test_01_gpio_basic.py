#!/usr/bin/env python3
"""
Test 1: GPIO Basic Functionality
Verifica che lgpio funzioni correttamente
"""

import lgpio as GPIO  # Sostituito RPi.GPIO con lgpio
import sys

# Mappatura dei valori per chiarezza con lgpio
HIGH = 1
LOW = 0
IN = 0  # Non usato direttamente, ma per chiarezza
OUT = 1

def test_gpio_basic():
    print("\n" + "="*70)
    print("TEST 1: GPIO BASIC FUNCTIONALITY")
    print("="*70 + "\n")

    gpio_handle = None

    try:
        # Test apertura chip GPIO
        print("1. Testing GPIO.gpiochip_open(0)...", end=" ")
        gpio_handle = GPIO.gpiochip_open(0)
        print("✓ OK")

        # GPIO.setmode() e GPIO.setwarnings() non sono necessari con lgpio

        # Test setup output
        print("2. Testing GPIO.gpio_claim_output(H, 18)...", end=" ")
        GPIO.gpio_claim_output(gpio_handle, 18)
        print("✓ OK")

        # Test output high
        print("3. Testing GPIO.gpio_write(H, 18, HIGH)...", end=" ")
        GPIO.gpio_write(gpio_handle, 18, HIGH)
        print("✓ OK")

        # Test output low
        print("4. Testing GPIO.gpio_write(H, 18, LOW)...", end=" ")
        GPIO.gpio_write(gpio_handle, 18, LOW)
        print("✓ OK")

        # Test setup input
        print("5. Testing GPIO.gpio_claim_input(H, 14)...", end=" ")
        GPIO.gpio_claim_input(gpio_handle, 14, GPIO.SET_PULL_DOWN)
        print("✓ OK")

        # Test input
        print("6. Testing GPIO.gpio_read(H, 14)...", end=" ")
        value = GPIO.gpio_read(gpio_handle, 14)
        print(f"✓ OK (value={value})")

        # Cleanup
        print("7. Testing GPIO.gpiochip_close(H)...", end=" ")
        GPIO.gpiochip_close(gpio_handle)
        gpio_handle = None
        print("✓ OK")

        print("\n" + "="*70)
        print("✓ ALL GPIO BASIC TESTS PASSED")
        print("="*70 + "\n")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        if gpio_handle is not None:
            GPIO.gpiochip_close(gpio_handle)
        return False

if __name__ == "__main__":
    success = test_gpio_basic()
    sys.exit(0 if success else 1)
