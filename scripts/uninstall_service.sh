#!/bin/bash

echo "Uninstalling ACR122U Keyboard Emulator service..."

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run as root"
  echo "Please run: sudo $0"
  exit 1
fi

# Stop and disable the service
systemctl stop acr122u-keyboard.service
systemctl disable acr122u-keyboard.service

# Remove the service file
rm -f /etc/systemd/system/acr122u-keyboard.service

# Reload systemd
systemctl daemon-reload

echo
echo "ACR122U Keyboard Emulator service has been uninstalled."
echo