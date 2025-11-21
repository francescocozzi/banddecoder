#!/usr/bin/env python3
"""
Run All Tests
Executes all hardware tests in sequence
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test modules
from tests import test_01_gpio_basic
from tests import test_02_single_relay
from tests import test_03_all_relays
from tests import test_04_bcd_input
from tests import test_05_software_i2c


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_all_tests():
    """Run all tests in sequence"""
    print_header("BAND DECODER - TEST SUITE")
    print("This will run all hardware tests in sequence.")
    print("Press CTRL+C at any time to abort.\n")

    input("Press ENTER to start tests...")

    results = {}

    # Test 1: GPIO Basic
    print_header("TEST 1: GPIO Basic Functionality")
    try:
        result = test_01_gpio_basic.test_gpio_basic()
        results['GPIO Basic'] = result
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        results['GPIO Basic'] = False

    if not results.get('GPIO Basic'):
        print("\n⚠ WARNING: Basic GPIO test failed!")
        response = input("Continue with remaining tests? (y/n): ")
        if response.lower() != 'y':
            return results

    # Test 2: Single Relay
    print_header("TEST 2: Single Relay Test")
    try:
        result = test_02_single_relay.test_single_relay()
        results['Single Relay'] = result
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        results['Single Relay'] = False

    if not results.get('Single Relay'):
        print("\n⚠ WARNING: Single relay test failed!")
        response = input("Continue with remaining tests? (y/n): ")
        if response.lower() != 'y':
            return results

    # Test 3: All Relays
    print_header("TEST 3: All Relays Sequential Test")
    try:
        import lgpio
        gpio_h = lgpio.gpiochip_open(0)
        result = test_03_all_relays.test_all_relays(gpio_h)
        lgpio.gpiochip_close(gpio_h)
        results['All Relays'] = result
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        results['All Relays'] = False

    # Test 4: BCD Input (optional - requires radio)
    print_header("TEST 4: BCD Input Test (Optional)")
    print("This test requires a radio connected and powered ON.")
    response = input("Do you want to run BCD input test? (y/n): ")

    if response.lower() == 'y':
        print("\nStarting BCD test... Press CTRL+C to stop")
        try:
            result = test_04_bcd_input.test_bcd_input()
            results['BCD Input'] = result
        except KeyboardInterrupt:
            print("\nBCD test stopped by user")
            results['BCD Input'] = None
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results['BCD Input'] = False
    else:
        print("⊘ BCD test skipped")
        results['BCD Input'] = None

    # Test 5: Software I2C (optional - for ICOM)
    print_header("TEST 5: Software I2C Test (Optional)")
    print("This test is for ICOM radio support (ADS1115).")
    response = input("Do you want to run I2C test? (y/n): ")

    if response.lower() == 'y':
        try:
            result = test_05_software_i2c.test_software_i2c()
            results['Software I2C'] = result
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results['Software I2C'] = False
    else:
        print("⊘ I2C test skipped")
        results['Software I2C'] = None

    return results


def print_summary(results):
    """Print test results summary"""
    print_header("TEST SUMMARY")

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in results.items():
        if result is True:
            status = "✓ PASSED"
            passed += 1
        elif result is False:
            status = "✗ FAILED"
            failed += 1
        else:
            status = "⊘ SKIPPED"
            skipped += 1

        print(f"  {test_name:25s} {status}")

    print("\n" + "-" * 70)
    print(f"  Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("-" * 70 + "\n")

    if failed == 0 and passed > 0:
        print("✓ All required tests passed!")
        print("\nNext steps:")
        print("  1. Review configuration: config/settings.yaml")
        print("  2. Run band decoder: sudo python3 src/band_decoder.py")
        return True
    elif failed > 0:
        print("✗ Some tests failed. Please check hardware connections.")
        print("\nTroubleshooting:")
        print("  - Verify GPIO connections")
        print("  - Check relay board power supply")
        print("  - Ensure correct pin mappings in config")
        return False
    else:
        print("⊘ No tests were run")
        return False


def main():
    """Main entry point"""
    try:
        results = run_all_tests()
        success = print_summary(results)
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n⚠ Test suite interrupted by user")
        return 130

    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
