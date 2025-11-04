#!/usr/bin/env python3
"""
Test 2: Single Relay Test
Testa un singolo relè per verificare cablaggio
"""

import RPi.GPIO as GPIO
import time
import sys

RELAY_PIN = 18  # Primo relè scheda 1 (GPIO18, Pin 12)

def test_single_relay():
    print("\n" + "="*70)
    print("TEST 2: SINGLE RELAY TEST")
    print("="*70)
    print(f"\nTesting Relay on GPIO{RELAY_PIN} (Physical Pin 12)")
    print("Watch/Listen for relay click!\n")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    
    try:
        for i in range(5):
            print(f"\nCycle {i+1}/5:")
            
            # ON
            print("  Relay ON  (GPIO LOW)...", end=" ")
            GPIO.output(RELAY_PIN, GPIO.LOW)
            time.sleep(0.5)
            print("✓")
            
            # OFF
            print("  Relay OFF (GPIO HIGH)...", end=" ")
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            time.sleep(0.5)
            print("✓")
        
        print("\n" + "="*70)
        print("✓ SINGLE RELAY TEST COMPLETED")
        print("="*70)
        print("\nDid you hear/see the relay clicking?")
        response = input("(y/n): ").strip().lower()
        
        GPIO.cleanup()
        
        if response == 'y':
            print("\n✓ TEST PASSED - Relay working correctly!")
            return True
        else:
            print("\n✗ TEST FAILED - Check wiring!")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        GPIO.cleanup()
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        GPIO.cleanup()
        return False

if __name__ == "__main__":
    success = test_single_relay()
    sys.exit(0 if success else 1)
