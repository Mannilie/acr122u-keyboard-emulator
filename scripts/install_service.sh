#!/bin/bash

echo "Installing ACR122U Keyboard Emulator as a Linux service..."

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run as root"
  echo "Please run: sudo $0"
  exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Create a Python virtual environment if it doesn't exist
if [ ! -d "$PARENT_DIR/venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$PARENT_DIR/venv"
fi

# Activate the virtual environment and install dependencies
source "$PARENT_DIR/venv/bin/activate"
pip install -r "$PARENT_DIR/requirements.txt"

# Create the systemd service file
cat > /etc/systemd/system/acr122u-keyboard.service << EOF
[Unit]
Description=ACR122U NFC Keyboard Emulator
After=pcscd.service
Wants=pcscd.service

[Service]
ExecStart=$PARENT_DIR/venv/bin/python $PARENT_DIR/main.py
WorkingDirectory=$PARENT_DIR
Restart=always
RestartSec=5
User=root
Group=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Create logs directory
mkdir -p "$PARENT_DIR/logs"

# Reload systemd, enable and start the service
systemctl daemon-reload
systemctl enable acr122u-keyboard.service
systemctl start acr122u-keyboard.service

echo
echo "ACR122U Keyboard Emulator service has been installed and started."
echo "To check status: systemctl status acr122u-keyboard.service"
echo "To view logs: journalctl -u acr122u-keyboard.service"
echo
echo "To uninstall, run: sudo ./uninstall_service.sh"
echo