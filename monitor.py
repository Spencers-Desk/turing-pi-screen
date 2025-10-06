#!/usr/bin/env python3
"""
Turing Pi 2 Screen Monitor
Main program for displaying cluster metrics on an OLED screen.
"""
import yaml
import time
import signal
import sys
import os
from pathlib import Path

from display_driver import DisplayDriver
from remote_collector import RemoteCollector
from metrics_collector import get_local_metrics


class ScreenMonitor:
    """
    Main screen monitor application.
    """
    
    def __init__(self, config_file='config.yaml'):
        """
        Initialize the screen monitor.
        
        Args:
            config_file (str): Path to configuration file
        """
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize display
        display_config = self.config['display']
        self.display = DisplayDriver(
            port=display_config['i2c_port'],
            address=display_config['i2c_address'],
            width=display_config['width'],
            height=display_config['height'],
            rotate=display_config['rotate']
        )
        
        # Initialize remote collector
        ssh_config = self.config['ssh']
        self.remote_collector = RemoteCollector(
            ssh_key_file=ssh_config.get('key_file'),
            timeout=ssh_config.get('timeout', 5)
        )
        
        # Update interval
        self.update_interval = self.config.get('update_interval', 2)
        
        # Running flag
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        print("\nShutting down...")
        self.running = False
    
    def collect_all_metrics(self):
        """
        Collect metrics from all nodes including local node.
        
        Returns:
            dict: Dictionary of all node metrics
        """
        # Get metrics from remote nodes
        metrics = self.remote_collector.get_all_nodes_metrics(
            self.config['nodes']
        )
        
        # Add local node (node4) metrics
        try:
            local_metrics = get_local_metrics()
            metrics['node4'] = local_metrics
        except Exception as e:
            print(f"Error getting local metrics: {e}")
            metrics['node4'] = None
        
        return metrics
    
    def run(self):
        """
        Main monitoring loop.
        """
        print("Starting Turing Pi 2 Screen Monitor...")
        self.running = True
        
        # Show loading screen
        self.display.display_loading()
        time.sleep(1)
        
        while self.running:
            try:
                # Collect metrics from all nodes
                metrics = self.collect_all_metrics()
                
                # Display metrics
                self.display.display_metrics(metrics)
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)
        
        # Cleanup
        self.display.clear()
        print("Monitor stopped.")
    
    def toggle_display(self):
        """Toggle the display on/off."""
        if self.display.is_on:
            self.display.turn_off()
            print("Display turned off")
        else:
            self.display.turn_on()
            print("Display turned on")


def main():
    """Main entry point."""
    # Check for config file
    config_file = 'config.yaml'
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found!")
        print("Please create a config.yaml file with your node settings.")
        sys.exit(1)
    
    # Create and run monitor
    monitor = ScreenMonitor(config_file)
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
