#!/bin/bash
# Band Decoder Uninstallation Script

set -e

echo "========================================================================"
echo "DUAL BAND DECODER - Uninstall Script"
echo "========================================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root!"
    echo "Run as: ./scripts/uninstall.sh"
    exit 1
fi

echo "This will remove the band decoder systemd services."
read -p "Are you sure you want to continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi
echo ""

# Stop services
echo "1. Stopping services..."
sudo systemctl stop banddecoder.service 2>/dev/null || true
sudo systemctl stop banddecoder-web.service 2>/dev/null || true
echo "✓ Services stopped"
echo ""

# Disable services
echo "2. Disabling services..."
sudo systemctl disable banddecoder.service 2>/dev/null || true
sudo systemctl disable banddecoder-web.service 2>/dev/null || true
echo "✓ Services disabled"
echo ""

# Remove service files
echo "3. Removing service files..."
sudo rm -f /etc/systemd/system/banddecoder.service
sudo rm -f /etc/systemd/system/banddecoder-web.service
echo "✓ Service files removed"
echo ""

# Reload systemd
echo "4. Reloading systemd..."
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

echo "========================================================================"
echo "UNINSTALL COMPLETE!"
echo "========================================================================"
echo ""
echo "Note: Project files and configuration were NOT removed."
echo "To completely remove the project, delete the project directory manually."
echo ""
echo "Log file location: /var/log/banddecoder.log"
echo ""
