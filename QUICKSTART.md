# Turing Pi Screen Monitor - Quick Reference

## Installation

```bash
# Clone the repository
git clone https://github.com/Spencers-Desk/turing-pi-screen.git
cd turing-pi-screen

# Run the setup script
./setup.sh

# Edit configuration
nano config.yaml

# Run diagnostics
python3 diagnose.py
```

## Configuration

Edit `config.yaml` to set:
- Node IP addresses and SSH usernames
- Display I2C port and address
- Update interval
- SSH key path

## Running

```bash
# Run manually
python3 monitor.py

# Install as service
sudo cp turing-pi-screen.service /etc/systemd/system/
sudo systemctl enable turing-pi-screen
sudo systemctl start turing-pi-screen
```

## Display Control

```bash
# Toggle display on/off
python3 control_display.py toggle

# Check status
python3 control_display.py status

# Service control
sudo systemctl start turing-pi-screen   # Start
sudo systemctl stop turing-pi-screen    # Stop
sudo systemctl restart turing-pi-screen # Restart
```

## Troubleshooting

```bash
# Run diagnostics
python3 diagnose.py

# View service logs
sudo journalctl -u turing-pi-screen -f

# Test components
python3 test_components.py

# Check I2C
sudo i2cdetect -y 1

# Test SSH connection
ssh pi@NODE_IP
```

## Display Format

```
hostname  CPU%  MEM%  TEMP
pi-node1  45%   62%   52C
pi-node2  24%   48%   49C
pi-node3  67%   75%   56C
pi-node4  12%   35%   45C
```

## Files

- `monitor.py` - Main monitoring program
- `display_driver.py` - OLED display driver
- `metrics_collector.py` - Local metrics collection
- `remote_collector.py` - Remote SSH-based collection
- `control_display.py` - Display control utility
- `diagnose.py` - Diagnostic tool
- `test_components.py` - Component test utility
- `setup.sh` - Installation script
- `config.yaml` - Configuration file
- `turing-pi-screen.service` - Systemd service file

## Common Issues

### Display not working
- Check I2C is enabled: `sudo raspi-config`
- Verify display address: `sudo i2cdetect -y 1`
- Check connection to GPIO pins

### Cannot connect to nodes
- Verify IP addresses in config.yaml
- Set up SSH keys: `ssh-copy-id pi@NODE_IP`
- Test SSH manually: `ssh pi@NODE_IP`

### High CPU usage
- Increase `update_interval` in config.yaml
- Check for network issues

### Temperature not showing
- Normal on some systems
- Temperature sensor may not be accessible
