#!/usr/bin/env python3
"""
Diagnostic script to help troubleshoot Turing Pi screen monitor issues.
"""
import sys
import os
import subprocess


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def check_python():
    """Check Python version."""
    print_section("Python Version")
    print(f"Python: {sys.version}")
    if sys.version_info < (3, 7):
        print("⚠ Warning: Python 3.7+ is recommended")
        return False
    print("✓ Python version OK")
    return True


def check_dependencies():
    """Check if required Python packages are installed."""
    print_section("Python Dependencies")
    
    packages = ['psutil', 'paramiko', 'yaml', 'PIL']
    all_ok = True
    
    for package in packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            elif package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_ok = False
    
    # Check optional display libraries
    try:
        from luma.oled.device import ssd1309
        print("✓ luma.oled")
    except ImportError:
        print("⚠ luma.oled - NOT INSTALLED (display will not work)")
    
    return all_ok


def check_config():
    """Check configuration file."""
    print_section("Configuration")
    
    if not os.path.exists('config.yaml'):
        print("✗ config.yaml NOT FOUND")
        print("  Run: cp config.example.yaml config.yaml")
        return False
    
    print("✓ config.yaml exists")
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check nodes
        if 'nodes' in config:
            print(f"  Configured nodes: {len(config['nodes'])}")
            for node, info in config['nodes'].items():
                print(f"    - {node}: {info.get('user')}@{info.get('ip')}")
        
        # Check display
        if 'display' in config:
            display = config['display']
            print(f"  Display: I2C port {display.get('i2c_port')}, "
                  f"address 0x{display.get('i2c_address', 0):02X}")
        
        return True
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False


def check_i2c():
    """Check I2C setup."""
    print_section("I2C Configuration")
    
    # Check if I2C devices exist
    if os.path.exists('/dev/i2c-1'):
        print("✓ /dev/i2c-1 exists")
    else:
        print("✗ /dev/i2c-1 not found")
        print("  Enable I2C: sudo raspi-config -> Interface Options -> I2C")
        return False
    
    # Try to detect I2C devices
    try:
        result = subprocess.run(
            ['i2cdetect', '-y', '1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ I2C bus accessible")
            print("\nI2C Device Map:")
            print(result.stdout)
            return True
        else:
            print("✗ Cannot access I2C bus")
            print("  You may need to run with sudo or add user to i2c group:")
            print("  sudo usermod -a -G i2c $USER")
            return False
    except FileNotFoundError:
        print("⚠ i2cdetect not found")
        print("  Install: sudo apt-get install i2c-tools")
        return False
    except subprocess.TimeoutExpired:
        print("✗ I2C bus timeout")
        return False


def check_ssh():
    """Check SSH configuration."""
    print_section("SSH Configuration")
    
    ssh_key = os.path.expanduser("~/.ssh/id_rsa")
    if os.path.exists(ssh_key):
        print(f"✓ SSH key found: {ssh_key}")
    else:
        print(f"✗ SSH key not found: {ssh_key}")
        print("  Generate: ssh-keygen -t rsa -b 4096")
        return False
    
    # Check SSH agent
    if 'SSH_AUTH_SOCK' in os.environ:
        print("✓ SSH agent is running")
    else:
        print("⚠ SSH agent may not be running")
        print("  Start: eval $(ssh-agent) && ssh-add")
    
    return True


def test_local_metrics():
    """Test local metrics collection."""
    print_section("Local Metrics Test")
    
    try:
        from metrics_collector import get_local_metrics
        metrics = get_local_metrics()
        
        print(f"✓ Hostname: {metrics.get('hostname')}")
        print(f"  CPU: {metrics.get('cpu_percent')}%")
        print(f"  Memory: {metrics.get('memory_percent')}%")
        print(f"  Temperature: {metrics.get('temperature')}°C")
        
        return True
    except Exception as e:
        print(f"✗ Error collecting metrics: {e}")
        return False


def test_remote_connection():
    """Test SSH connection to configured nodes."""
    print_section("Remote Connection Test")
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        from remote_collector import RemoteCollector
        collector = RemoteCollector(
            ssh_key_file=config['ssh'].get('key_file'),
            timeout=5
        )
        
        for node_name, node_config in config['nodes'].items():
            print(f"\nTesting {node_name} ({node_config['ip']})...")
            metrics = collector.get_remote_metrics(
                node_config['ip'],
                node_config['user']
            )
            
            if metrics:
                print(f"  ✓ Connection successful")
                print(f"    Hostname: {metrics.get('hostname')}")
                print(f"    CPU: {metrics.get('cpu_percent')}%")
            else:
                print(f"  ✗ Connection failed")
        
        return True
    except Exception as e:
        print(f"✗ Error testing remote connections: {e}")
        return False


def check_service():
    """Check systemd service status."""
    print_section("Service Status")
    
    try:
        result = subprocess.run(
            ['systemctl', 'is-enabled', 'turing-pi-screen'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Service is enabled")
        else:
            print("⚠ Service is not enabled")
            print("  Enable: sudo systemctl enable turing-pi-screen")
        
        result = subprocess.run(
            ['systemctl', 'is-active', 'turing-pi-screen'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Service is running")
        else:
            print("⚠ Service is not running")
            print("  Start: sudo systemctl start turing-pi-screen")
        
        return True
    except FileNotFoundError:
        print("⚠ systemctl not available")
        return False


def main():
    """Run all diagnostics."""
    print("=" * 60)
    print("Turing Pi Screen Monitor - Diagnostics")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python),
        ("Python Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("I2C", check_i2c),
        ("SSH", check_ssh),
        ("Local Metrics", test_local_metrics),
        ("Remote Connections", test_remote_connection),
        ("Service Status", check_service),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Diagnostic Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:25} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! System is ready.")
        return 0
    else:
        print("\n⚠ Some checks failed. Review the output above for details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
