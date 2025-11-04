#!/usr/bin/env python3
"""
Test 4: BCD Input Test
Legge input BCD dalle radio
RICHIEDE: Radio collegata e accesa
"""

import RPi.GPIO as GPIO
import time
import sys

# Pin BCD (dal tuo cablaggio)
RADIO1_BCD = {'D0': 14, 'D1': 15, 'D2': 10, 'D3': 9}
RADIO2_BCD = {'D0': 13, 'D1': 19, 'D2': 26, 'D3': 11}

BANDS = {
    1: "160m", 2: "80m", 3: "60m", 4: "40m", 5: "30m",
    6: "20m", 7: "17m", 8: "15m", 9: "12m", 10: "10m",
    11: "6m", 12: "4m", 13: "2m", 14: "70cm", 15: "23cm"
}

def read_bcd(pins_dict):
    """Leggi valore BCD da 4 pin"""
    d0 = GPIO.input(pins_dict['D0'])
    d1 = GPIO.input(pins_dict['D1'])
    d2 = GPIO.input(pins_dict['D2'])
    d3 = GPIO.input(pins_dict['D3'])
    return d0 + (d1 << 1) + (d2 << 2) + (d3 << 3)

def test_bcd_input():
    print("\n" + "="*70)
    print("TEST 4: BCD INPUT TEST")
    print("="*70)
    print("\n⚠️  REQUIREMENTS:")
    print("   - Radio(s) must be connected")
    print("   - Radio(s) must be powered ON")
    print("   - BCD cables must be connected")
    print("\nPress CTRL+C to stop\n")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup BCD inputs
    print("Setting up BCD inputs...")
    for pin in RADIO1_BCD.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    for pin in RADIO2_BCD.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print("✓ BCD inputs configured\n")
    
    time.sleep(0.5)
    
    print("Reading BCD values...")
    print("Change band on radio to see values update\n")
    print("-" * 70)
    
    last_r1 = None
    last_r2 = None
    
    try:
        while True:
            # Read Radio 1
            bcd1 = read_bcd(RADIO1_BCD)
            d0_1 = GPIO.input(RADIO1_BCD['D0'])
            d1_1 = GPIO.input(RADIO1_BCD['D1'])
            d2_1 = GPIO.input(RADIO1_BCD['D2'])
            d3_1 = GPIO.input(RADIO1_BCD['D3'])
            
            # Read Radio 2
            bcd2 = read_bcd(RADIO2_BCD)
            d0_2 = GPIO.input(RADIO2_BCD['D0'])
            d1_2 = GPIO.input(RADIO2_BCD['D1'])
            d2_2 = GPIO.input(RADIO2_BCD['D2'])
            d3_2 = GPIO.input(RADIO2_BCD['D3'])
            
            # Get band names
            band1 = BANDS.get(bcd1, "???")
            band2 = BANDS.get(bcd2, "???")
            
            # Print if changed
            if bcd1 != last_r1 or bcd2 != last_r2:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}]")
                print(f"  Radio 1: BCD={bcd1:2d} ({d3_1}{d2_1}{d1_1}{d0_1}) → {band1:5s}")
                print(f"  Radio 2: BCD={bcd2:2d} ({d3_2}{d2_2}{d1_2}{d0_2}) → {band2:5s}")
                print()
                
                last_r1 = bcd1
                last_r2 = bcd2
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n" + "-" * 70)
        print("\n✓ BCD INPUT TEST COMPLETED")
        print("\nFinal readings:")
        print(f"  Radio 1: BCD={bcd1} → {band1}")
        print(f"  Radio 2: BCD={bcd2} → {band2}")
        
        GPIO.cleanup()
        
        if bcd1 > 0 or bcd2 > 0:
            print("\n✓ TEST PASSED - BCD input working!")
            return True
        else:
            print("\n⚠️  WARNING: No BCD signal detected")
            print("\nCheck:")
            print("  1. Radio is ON")
            print("  2. BCD output enabled on radio")
            print("  3. Cables connected to correct pins")
            print("  4. 1kΩ resistors in place")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        GPIO.cleanup()
        return False

if __name__ == "__main__":
    success = test_bcd_input()
    sys.exit(0 if success else 1)
