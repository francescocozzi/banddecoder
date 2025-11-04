#!/usr/bin/env python3
"""
Test 5: Software I2C Basic Test
Testa comunicazione I2C software (senza ADS1115)
"""

import RPi.GPIO as GPIO
import time
import sys

I2C_SDA_PIN = 5
I2C_SCL_PIN = 6

class SoftwareI2C:
    def __init__(self, sda_pin, scl_pin):
        self.sda = sda_pin
        self.scl = scl_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sda, GPIO.OUT)
        GPIO.setup(self.scl, GPIO.OUT)
        GPIO.output(self.sda, GPIO.HIGH)
        GPIO.output(self.scl, GPIO.HIGH)
        self.delay = 0.00001
    
    def _sda_high(self):
        GPIO.setup(self.sda, GPIO.IN)
        time.sleep(self.delay)
    
    def _sda_low(self):
        GPIO.setup(self.sda, GPIO.OUT)
        GPIO.output(self.sda, GPIO.LOW)
        time.sleep(self.delay)
    
    def _scl_high(self):
        GPIO.output(self.scl, GPIO.HIGH)
        time.sleep(self.delay)
    
    def _scl_low(self):
        GPIO.output(self.scl, GPIO.LOW)
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
    
    try:
        print("1. Initializing Software I2C...", end=" ")
        i2c = SoftwareI2C(I2C_SDA_PIN, I2C_SCL_PIN)
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
        
        GPIO.cleanup()
        
        print("\n" + "="*70)
        print("✓ SOFTWARE I2C BASIC TEST PASSED")
        print("="*70)
        print("\nNote: This only tests I2C timing, not device communication")
        print("ADS1115 test will come next\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        GPIO.cleanup()
        return False

if __name__ == "__main__":
    success = test_software_i2c()
    sys.exit(0 if success else 1)
