#!/bin/bash
# Quick setup script for Turing Pi 2 Screen Monitor
# Run this on Node 4 (the node with the OLED screen)

set -e

echo "================================================"
echo "Turing Pi 2 Screen Monitor - Quick Setup"
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "This script is designed for Raspberry Pi CM4 modules"
    echo ""
fi

# Install system dependencies
echo "Step 1: Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev i2c-tools

# Enable I2C
echo ""
echo "Step 2: Enabling I2C..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    echo "I2C enabled in /boot/config.txt"
    echo "A reboot will be required after setup"
    REBOOT_NEEDED=1
fi

# Load I2C module for current session
sudo modprobe i2c-dev || true

# Install Python dependencies
echo ""
echo "Step 3: Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Setup SSH keys if needed
echo ""
echo "Step 4: Checking SSH key setup..."
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "No SSH key found. Generating one..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo "SSH key generated at ~/.ssh/id_rsa"
    echo ""
    echo "IMPORTANT: You need to copy this key to your other nodes:"
    echo "  ssh-copy-id pi@NODE1_IP"
    echo "  ssh-copy-id pi@NODE2_IP"
    echo "  ssh-copy-id pi@NODE3_IP"
else
    echo "SSH key already exists at ~/.ssh/id_rsa"
fi

# Create config from example if it doesn't exist
echo ""
echo "Step 5: Setting up configuration..."
if [ ! -f config.yaml ]; then
    cp config.example.yaml config.yaml
    echo "Created config.yaml from example"
    echo ""
    echo "IMPORTANT: Edit config.yaml and update the node IP addresses:"
    echo "  nano config.yaml"
else
    echo "config.yaml already exists"
fi

# Test I2C
echo ""
echo "Step 6: Testing I2C connection..."
if command -v i2cdetect &> /dev/null; then
    echo "I2C devices found:"
    sudo i2cdetect -y 1 || echo "Note: I2C may require a reboot to work"
else
    echo "i2cdetect not available"
fi

# Test the installation
echo ""
echo "Step 7: Testing installation..."
python3 test_components.py || true

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your node IP addresses:"
echo "   nano config.yaml"
echo ""
echo "2. Copy SSH keys to your other nodes:"
echo "   ssh-copy-id pi@NODE_IP"
echo ""
echo "3. Test the monitor:"
echo "   python3 monitor.py"
echo ""
echo "4. Install as a service (optional):"
echo "   sudo cp turing-pi-screen.service /etc/systemd/system/"
echo "   sudo systemctl enable turing-pi-screen.service"
echo "   sudo systemctl start turing-pi-screen.service"
echo ""

if [ "$REBOOT_NEEDED" = "1" ]; then
    echo "================================================"
    echo "REBOOT REQUIRED"
    echo "================================================"
    echo "I2C was just enabled. Please reboot before using:"
    echo "  sudo reboot"
    echo ""
fi
