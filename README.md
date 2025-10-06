# turing-pi-screen
A screen for monitoring your Turing Pi 2 Raspberry Pi Cluster.

## Overview

This project provides a Python-based monitoring solution for Turing Pi 2 clusters with Raspberry Pi CM4 nodes. It displays real-time metrics including CPU usage, memory usage, temperature, and hostname for each node on a 2.42" OLED-IIC screen (SSD1309 driver).

**Quick Start:** See [QUICKSTART.md](QUICKSTART.md) for a condensed reference guide.

### Features

- **Multi-Node Monitoring**: Query and display metrics from all nodes (1-3) from node 4
- **Real-Time Metrics**: CPU usage, memory usage, temperature, and hostname
- **OLED Display**: Support for SSD1309 2.42" OLED screen via I2C
- **Remote Collection**: SSH-based remote metrics collection
- **Display Control**: Ability to turn the screen on/off
- **Auto-Start**: Systemd service for automatic startup
- **Configurable**: YAML-based configuration for easy customization

## Hardware Requirements

- Turing Pi 2 board with Raspberry Pi CM4 modules
- 2.42" OLED-IIC screen with SSD1309 driver
- I2C connection between Node 4 and the OLED screen

## Software Requirements

- Python 3.7+
- I2C enabled on Node 4
- SSH access configured between nodes (passwordless SSH recommended)

## Installation

### 1. Clone the Repository

On Node 4 (the node with the screen attached):

```bash
cd ~
git clone https://github.com/Spencers-Desk/turing-pi-screen.git
cd turing-pi-screen
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Enable I2C

Ensure I2C is enabled on Node 4:

```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
```

Verify I2C is working:

```bash
sudo i2cdetect -y 1
```

You should see the display at address 0x3C.

### 4. Configure SSH Keys

For passwordless SSH between nodes, set up SSH keys:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096

# Copy the key to each node
ssh-copy-id pi@192.168.1.101  # Node 1
ssh-copy-id pi@192.168.1.102  # Node 2
ssh-copy-id pi@192.168.1.103  # Node 3
```

### 5. Configure the Application

Edit `config.yaml` to match your cluster setup:

```yaml
nodes:
  node1:
    ip: "192.168.1.101"  # Update with your node's IP
    user: "pi"
  node2:
    ip: "192.168.1.102"
    user: "pi"
  node3:
    ip: "192.168.1.103"
    user: "pi"

display:
  i2c_port: 1
  i2c_address: 0x3C
  width: 128
  height: 64
  rotate: 0

update_interval: 2

ssh:
  key_file: "~/.ssh/id_rsa"
  timeout: 5
```

### 6. Test the Application

Run diagnostics to check your setup:

```bash
python3 diagnose.py
```

Run the monitor manually to test:

```bash
python3 monitor.py
```

You should see metrics displayed on the OLED screen. Press Ctrl+C to stop.

### 7. Install as a Service (Optional)

To run the monitor automatically on boot:

```bash
# Copy the service file
sudo cp turing-pi-screen.service /etc/systemd/system/

# Edit the service file if your paths are different
sudo nano /etc/systemd/system/turing-pi-screen.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable turing-pi-screen.service
sudo systemctl start turing-pi-screen.service

# Check status
sudo systemctl status turing-pi-screen.service
```

## Usage

### Running Manually

```bash
cd ~/turing-pi-screen
python3 monitor.py
```

### Display Control

The display can be controlled while the monitor is running:

```bash
# Toggle the display on/off (keeps monitor running)
python3 control_display.py toggle

# Or send the signal directly
kill -SIGUSR1 $(pgrep -f monitor.py)

# Check monitor status
python3 control_display.py status

# Start/stop the monitor service
sudo python3 control_display.py on
sudo python3 control_display.py off
```

### Service Management

```bash
# Start the service
sudo systemctl start turing-pi-screen

# Stop the service
sudo systemctl stop turing-pi-screen

# Restart the service
sudo systemctl restart turing-pi-screen

# Check status
sudo systemctl status turing-pi-screen

# View logs
sudo journalctl -u turing-pi-screen -f
```

### Display Format

The screen displays one line per node with the following format:

```
hostname CPU% MEM% TEMP
```

Example:
```
pi-node1  45%  62%  52C
pi-node2  24%  48%  49C
pi-node3  67%  75%  56C
pi-node4  12%  35%  45C
```

## Modules

### Core Files

- **`monitor.py`** - Main application that coordinates metrics collection and display updates
- **`display_driver.py`** - OLED display driver for SSD1309 screens with on/off control
- **`metrics_collector.py`** - Local system metrics collection using psutil
- **`remote_collector.py`** - SSH-based remote metrics collection from other nodes
- **`config.yaml`** - Configuration file for node IPs, display settings, and SSH parameters

### Utilities

- **`control_display.py`** - Command-line utility to control display (on/off/toggle/status)
- **`diagnose.py`** - Diagnostic tool to troubleshoot installation and configuration issues
- **`test_components.py`** - Component test utility to verify individual modules
- **`setup.sh`** - Automated setup script for quick installation

### Configuration Files

- **`config.yaml`** - Main configuration (created from config.example.yaml)
- **`config.example.yaml`** - Example configuration template
- **`turing-pi-screen.service`** - Systemd service file for auto-start

## Troubleshooting

### Display Not Working

1. Check I2C connection:
   ```bash
   sudo i2cdetect -y 1
   ```

2. Verify display address in config.yaml (typically 0x3C or 0x3D)

3. Check I2C is enabled:
   ```bash
   ls /dev/i2c-*
   ```

### SSH Connection Issues

1. Test manual SSH connection:
   ```bash
   ssh pi@192.168.1.101
   ```

2. Verify SSH keys are set up:
   ```bash
   ssh -v pi@192.168.1.101
   ```

3. Check SSH agent is running:
   ```bash
   eval $(ssh-agent)
   ssh-add ~/.ssh/id_rsa
   ```

### High CPU Usage

Increase the `update_interval` in config.yaml to reduce update frequency.

### Node Shows as OFFLINE

1. Check node is powered on and accessible
2. Verify IP address in config.yaml
3. Test SSH connection manually
4. Check firewall settings on the remote node

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the Turing Pi 2 cluster board
- Uses the luma.oled library for display control
- Inspired by the need for simple, effective cluster monitoring
