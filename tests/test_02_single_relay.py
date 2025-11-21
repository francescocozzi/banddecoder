#!/usr/bin/env python3
"""
Test 2: Single Relay Test
Testa un singolo relè per verificare cablaggio
"""

import lgpio as GPIO  # Sostituito RPi.GPIO con lgpio
import time
import sys

# Mappatura dei valori per chiarezza con lgpio
HIGH = 1
LOW = 0

RELAY_PIN = 18  # Primo relè scheda 1 (GPIO18, Pin 12)

def test_single_relay():
    print("\n" + "="*70)
    print("TEST 2: SINGLE RELAY TEST")
    print("="*70)
    print(f"\nTesting Relay on GPIO{RELAY_PIN} (Physical Pin 12)")
    print("Watch/Listen for relay click!\n")

    gpio_handle = None

    try:
        # Apri il chip GPIO 0 (standard sul Raspberry Pi 5)
        gpio_handle = GPIO.gpiochip_open(0)

        # GPIO.setmode() e GPIO.setwarnings() non sono necessari con lgpio

        # Equivalente a GPIO.setup(RELAY_PIN, GPIO.OUT)
        GPIO.gpio_claim_output(gpio_handle, RELAY_PIN)

        for i in range(5):
            print(f"\nCycle {i+1}/5:")

            # ON
            print("  Relay ON  (GPIO LOW)...", end=" ")
            GPIO.gpio_write(gpio_handle, RELAY_PIN, LOW)
            time.sleep(0.5)
            print("✓")

            # OFF
            print("  Relay OFF (GPIO HIGH)...", end=" ")
            GPIO.gpio_write(gpio_handle, RELAY_PIN, HIGH)
            time.sleep(0.5)
            print("✓")

        print("\n" + "="*70)
        print("✓ SINGLE RELAY TEST COMPLETED")
        print("="*70)
        print("\nDid you hear/see the relay clicking?")
        response = input("(y/n): ").strip().lower()

        # Chiudi l'handle del chip GPIO (equivalente a GPIO.cleanup())
        if gpio_handle is not None:
            GPIO.gpiochip_close(gpio_handle)
            gpio_handle = None

        if response == 'y':
            print("\n✓ TEST PASSED - Relay working correctly!")
            return True
        else:
            print("\n✗ TEST FAILED - Check wiring!")
            return False

    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        if gpio_handle is not None:
            GPIO.gpiochip_close(gpio_handle)
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        if gpio_handle is not None:
            GPIO.gpiochip_close(gpio_handle)
        return False

if __name__ == "__main__":
    success = test_single_relay()
    sys.exit(0 if success else 1)
