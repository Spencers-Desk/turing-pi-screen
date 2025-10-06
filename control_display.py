#!/usr/bin/env python3
"""
Control script for turning the display on/off.
Send signals to the running monitor process to control the display.
"""
import sys
import os
import subprocess
import signal


def get_monitor_pid():
    """
    Get the PID of the running monitor process.
    
    Returns:
        int: PID of monitor process, or None if not found
    """
    try:
        # Try to get PID from systemd service
        result = subprocess.run(
            ['systemctl', 'show', '-p', 'MainPID', 'turing-pi-screen'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pid_line = result.stdout.strip()
            if pid_line.startswith('MainPID='):
                pid = int(pid_line.split('=')[1])
                if pid > 0:
                    return pid
    except (FileNotFoundError, ValueError):
        pass
    
    # Fallback: search for process
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'monitor.py'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            if pids and pids[0]:
                return int(pids[0])
    except (FileNotFoundError, ValueError):
        pass
    
    return None


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: control_display.py [on|off|toggle|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'toggle':
        # Send SIGUSR1 to toggle display
        pid = get_monitor_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGUSR1)
                print(f"Display toggle signal sent to process {pid}")
            except ProcessLookupError:
                print("Monitor process not found")
                sys.exit(1)
            except PermissionError:
                print("Permission denied. Try with sudo:")
                print(f"  sudo python3 control_display.py toggle")
                sys.exit(1)
        else:
            print("Monitor process not running")
            sys.exit(1)
    
    elif command == 'on':
        print("Starting monitor service...")
        result = subprocess.run(['sudo', 'systemctl', 'start', 'turing-pi-screen'])
        sys.exit(result.returncode)
    
    elif command == 'off':
        print("Stopping monitor service...")
        result = subprocess.run(['sudo', 'systemctl', 'stop', 'turing-pi-screen'])
        sys.exit(result.returncode)
    
    elif command == 'status':
        # Check if service is running
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'turing-pi-screen'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                pid = get_monitor_pid()
                print(f"Display monitor is RUNNING (PID: {pid})")
            else:
                print("Display monitor is STOPPED")
        except FileNotFoundError:
            print("systemctl not available - checking manually...")
            pid = get_monitor_pid()
            if pid:
                print(f"Monitor process found (PID: {pid})")
            else:
                print("Monitor process not found")
    
    else:
        print(f"Unknown command: {command}")
        print("Usage: control_display.py [on|off|toggle|status]")
        sys.exit(1)


if __name__ == '__main__':
    main()
