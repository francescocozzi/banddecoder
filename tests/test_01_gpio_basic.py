#!/usr/bin/env python3
"""
Test 1: GPIO Basic Functionality
Verifica che RPi.GPIO funzioni correttamente
"""

import RPi.GPIO as GPIO
import sys

def test_gpio_basic():
    print("\n" + "="*70)
    print("TEST 1: GPIO BASIC FUNCTIONALITY")
    print("="*70 + "\n")
    
    try:
        # Test setmode
        print("1. Testing GPIO.setmode(GPIO.BCM)...", end=" ")
        GPIO.setmode(GPIO.BCM)
        print("✓ OK")
        
        # Test warnings
        print("2. Testing GPIO.setwarnings(False)...", end=" ")
        GPIO.setwarnings(False)
        print("✓ OK")
        
        # Test setup output
        print("3. Testing GPIO.setup(18, GPIO.OUT)...", end=" ")
        GPIO.setup(18, GPIO.OUT)
        print("✓ OK")
        
        # Test output high
        print("4. Testing GPIO.output(18, GPIO.HIGH)...", end=" ")
        GPIO.output(18, GPIO.HIGH)
        print("✓ OK")
        
        # Test output low
        print("5. Testing GPIO.output(18, GPIO.LOW)...", end=" ")
        GPIO.output(18, GPIO.LOW)
        print("✓ OK")
        
        # Test setup input
        print("6. Testing GPIO.setup(14, GPIO.IN)...", end=" ")
        GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("✓ OK")
        
        # Test input
        print("7. Testing GPIO.input(14)...", end=" ")
        value = GPIO.input(14)
        print(f"✓ OK (value={value})")
        
        # Cleanup
        print("8. Testing GPIO.cleanup()...", end=" ")
        GPIO.cleanup()
        print("✓ OK")
        
        print("\n" + "="*70)
        print("✓ ALL GPIO BASIC TESTS PASSED")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        GPIO.cleanup()
        return False

if __name__ == "__main__":
    success = test_gpio_basic()
    sys.exit(0 if success else 1)
