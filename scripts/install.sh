#!/bin/bash
# Band Decoder Installation Script
# IZ7KHR - Ham Radio Station Controller

set -e

echo "========================================================================"
echo "DUAL BAND DECODER - Installation Script"
echo "IZ7KHR - Ham Radio Station Controller"
echo "========================================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root!"
    echo "Run as: ./scripts/install.sh"
    exit 1
fi

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Project directory: $PROJECT_DIR"
echo ""

# Update system
echo "1. Updating system packages..."
sudo apt update
echo "✓ System updated"
echo ""

# Install dependencies
echo "2. Installing system dependencies..."
sudo apt install -y python3-pip python3-dev git python3-lgpio
echo "✓ System dependencies installed"
echo ""

# Install Python packages
echo "3. Installing Python requirements..."
pip3 install -r "$PROJECT_DIR/requirements.txt"
echo "✓ Python packages installed"
echo ""

# Enable I2C (optional for ICOM radios)
echo "4. Checking I2C configuration..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "I2C not enabled. Would you like to enable it? (needed for ICOM radios)"
    read -p "Enable I2C? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo raspi-config nonint do_i2c 0
        echo "✓ I2C enabled (reboot required)"
    else
        echo "⚠ I2C not enabled (you can enable it later with raspi-config)"
    fi
else
    echo "✓ I2C already enabled"
fi
echo ""

# Install systemd services
echo "5. Installing systemd services..."

# Copy service files
sudo cp "$PROJECT_DIR/scripts/banddecoder.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/scripts/banddecoder-web.service" /etc/systemd/system/

# Update WorkingDirectory in service files to actual project path
sudo sed -i "s|/home/pi/banddecoder|$PROJECT_DIR|g" /etc/systemd/system/banddecoder.service
sudo sed -i "s|/home/pi/banddecoder|$PROJECT_DIR|g" /etc/systemd/system/banddecoder-web.service

# Reload systemd
sudo systemctl daemon-reload

echo "✓ Systemd services installed"
echo ""

# Ask to enable services
echo "6. Service configuration..."
read -p "Enable band decoder service to start at boot? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl enable banddecoder.service
    echo "✓ Band decoder service enabled"
else
    echo "⚠ Band decoder service not enabled"
fi

read -p "Enable web interface to start at boot? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl enable banddecoder-web.service
    echo "✓ Web interface service enabled"
else
    echo "⚠ Web interface service not enabled"
fi
echo ""

# Create log directory
echo "7. Creating log directory..."
sudo mkdir -p /var/log
sudo touch /var/log/banddecoder.log
sudo chown $USER:$USER /var/log/banddecoder.log
echo "✓ Log directory created"
echo ""

echo "========================================================================"
echo "INSTALLATION COMPLETE!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration:"
echo "   nano $PROJECT_DIR/config/settings.yaml"
echo ""
echo "2. Test hardware:"
echo "   sudo python3 $PROJECT_DIR/tests/test_01_gpio_basic.py"
echo "   sudo python3 $PROJECT_DIR/tests/test_02_single_relay.py"
echo ""
echo "3. Start services:"
echo "   sudo systemctl start banddecoder.service"
echo "   sudo systemctl start banddecoder-web.service"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status banddecoder.service"
echo "   sudo journalctl -u banddecoder.service -f"
echo ""
echo "5. Access web interface:"
echo "   http://$(hostname).local:5000"
echo "   or http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "73 de IZ7KHR!"
echo ""
