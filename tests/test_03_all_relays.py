#!/usr/bin/env python3
"""
Test 3: All Relays Sequential Test
Testa tutti i 16 relè in sequenza
"""

import RPi.GPIO as GPIO
import time
import sys

# Configurazione relè (dal tuo cablaggio)
RELAY1_PINS = [18, 23, 24, 25, 8, 7, 12, 16]  # Scheda 1
RELAY2_PINS = [20, 21, 2, 3, 4, 17, 27, 22]   # Scheda 2

BANDS = ["160m", "80m", "40m", "20m", "15m", "10m", "N/A", "N/A"]

def test_all_relays():
    print("\n" + "="*70)
    print("TEST 3: ALL RELAYS SEQUENTIAL TEST")
    print("="*70 + "\n")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup all relays
    print("Setting up relays...")
    all_pins = RELAY1_PINS + RELAY2_PINS
    for pin in all_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # All OFF
    print("✓ All relays initialized (OFF)\n")
    
    time.sleep(1)
    
    try:
        # Test Scheda 1
        print("BOARD 1 - Radio 1 Filters:")
        print("-" * 70)
        for i, pin in enumerate(RELAY1_PINS):
            band = BANDS[i] if i < 6 else "Spare"
            print(f"  Relay {i+1:2d} ({band:5s}) GPIO{pin:2d}: ", end="", flush=True)
            
            GPIO.output(pin, GPIO.LOW)   # ON
            print("ON  ", end="", flush=True)
            time.sleep(0.3)
            
            GPIO.output(pin, GPIO.HIGH)  # OFF
            print("→ OFF ✓")
            time.sleep(0.1)
        
        print()
        
        # Test Scheda 2
        print("BOARD 2 - Radio 2 Filters + Antenna:")
        print("-" * 70)
        for i, pin in enumerate(RELAY2_PINS):
            if i < 6:
                band = BANDS[i]
                desc = f"Radio 2 {band}"
            elif i == 6:
                desc = "Antenna R1"
            elif i == 7:
                desc = "Antenna R2"
            else:
                desc = "Spare"
            
            print(f"  Relay {i+9:2d} ({desc:15s}) GPIO{pin:2d}: ", end="", flush=True)
            
            GPIO.output(pin, GPIO.LOW)   # ON
            print("ON  ", end="", flush=True)
            time.sleep(0.3)
            
            GPIO.output(pin, GPIO.HIGH)  # OFF
            print("→ OFF ✓")
            time.sleep(0.1)
        
        print("\n" + "="*70)
        print("✓ ALL RELAYS TEST COMPLETED")
        print("="*70)
        print("\nDid all relays click properly?")
        response = input("(y/n): ").strip().lower()
        
        GPIO.cleanup()
        
        if response == 'y':
            print("\n✓ TEST PASSED - All relays working!")
            return True
        else:
            print("\n✗ TEST FAILED - Check relay wiring")
            print("\nTroubleshooting:")
            print("  1. Verify 5V power to both relay boards")
            print("  2. Check all GPIO connections")
            print("  3. Verify GND is common")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted")
        GPIO.cleanup()
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        GPIO.cleanup()
        return False

if __name__ == "__main__":
    success = test_all_relays()
    sys.exit(0 if success else 1)
