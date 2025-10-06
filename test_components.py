#!/usr/bin/env python3
"""
Test script for verifying individual components of the Turing Pi screen monitor.
"""
import sys
import os


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import psutil
        print("  ✓ psutil")
    except ImportError as e:
        print(f"  ✗ psutil: {e}")
        return False
    
    try:
        import paramiko
        print("  ✓ paramiko")
    except ImportError as e:
        print(f"  ✗ paramiko: {e}")
        return False
    
    try:
        import yaml
        print("  ✓ PyYAML")
    except ImportError as e:
        print(f"  ✗ PyYAML: {e}")
        return False
    
    try:
        from luma.oled.device import ssd1309
        from luma.core.interface.serial import i2c
        print("  ✓ luma.oled")
    except ImportError as e:
        print(f"  ✗ luma.oled: {e}")
        return False
    
    try:
        from PIL import Image
        print("  ✓ Pillow")
    except ImportError as e:
        print(f"  ✗ Pillow: {e}")
        return False
    
    return True


def test_config():
    """Test that config.yaml exists and is valid."""
    print("\nTesting configuration...")
    if not os.path.exists('config.yaml'):
        print("  ✗ config.yaml not found")
        return False
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required keys
        required_keys = ['nodes', 'display', 'update_interval', 'ssh']
        for key in required_keys:
            if key not in config:
                print(f"  ✗ Missing required key: {key}")
                return False
        
        print("  ✓ config.yaml is valid")
        return True
    except Exception as e:
        print(f"  ✗ Error reading config.yaml: {e}")
        return False


def test_local_metrics():
    """Test local metrics collection."""
    print("\nTesting local metrics collection...")
    try:
        from metrics_collector import get_local_metrics
        metrics = get_local_metrics()
        
        required_keys = ['hostname', 'cpu_percent', 'memory_percent']
        for key in required_keys:
            if key not in metrics:
                print(f"  ✗ Missing metric: {key}")
                return False
            print(f"  {key}: {metrics[key]}")
        
        print("  ✓ Local metrics collection working")
        return True
    except Exception as e:
        print(f"  ✗ Error collecting local metrics: {e}")
        return False


def test_i2c():
    """Test I2C connection."""
    print("\nTesting I2C connection...")
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ I2C bus accessible")
            print("\nI2C devices:")
            print(result.stdout)
            return True
        else:
            print("  ✗ Cannot access I2C bus")
            print("  Run: sudo raspi-config -> Interface Options -> I2C -> Enable")
            return False
    except FileNotFoundError:
        print("  ⚠ i2cdetect not found (install i2c-tools)")
        return False
    except Exception as e:
        print(f"  ✗ Error testing I2C: {e}")
        return False


def test_display():
    """Test display initialization."""
    print("\nTesting display initialization...")
    try:
        from display_driver import DisplayDriver
        display = DisplayDriver()
        
        if display.device is None:
            print("  ⚠ Display initialized in headless mode")
            print("  This is normal if no physical display is connected")
        else:
            print("  ✓ Display initialized successfully")
            display.display_text("Test OK!")
        
        return True
    except Exception as e:
        print(f"  ✗ Error initializing display: {e}")
        return False


def test_ssh_keys():
    """Test SSH key setup."""
    print("\nTesting SSH key setup...")
    ssh_key = os.path.expanduser("~/.ssh/id_rsa")
    if os.path.exists(ssh_key):
        print(f"  ✓ SSH key found: {ssh_key}")
        return True
    else:
        print(f"  ⚠ SSH key not found: {ssh_key}")
        print("  Run: ssh-keygen -t rsa -b 4096")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Turing Pi Screen Monitor - Component Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Local Metrics", test_local_metrics()))
    results.append(("I2C", test_i2c()))
    results.append(("Display", test_display()))
    results.append(("SSH Keys", test_ssh_keys()))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready.")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
