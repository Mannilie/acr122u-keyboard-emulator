# ACR122U NFC Reader to Keyboard Emulator

![License](https://img.shields.io/github/license/Mannilie/acr122u-keyboard-emulator)
![Version](https://img.shields.io/github/v/release/Mannilie/acr122u-keyboard-emulator)

A high-performance utility that converts ACR122U NFC reader card detections into keyboard input. Perfect for attendance systems, access control, or any application that requires NFC card data as keyboard input.

## Features

- 🚀 **High Performance**: Optimized for minimal latency between card read and keyboard output
- 🔄 **Multiple Reading Modes**: PC/SC, direct USB, and hybrid approaches for maximum compatibility
- ⚙️ **Highly Configurable**: Customize prefix, suffix, format, and more
- 🔌 **Easy Installation**: Simple setup as a system service
- 🔒 **Reliable**: Robust error handling and recovery
- 💻 **Cross-Platform**: Works on Windows, Linux, and macOS

## Requirements

- ACR122U NFC Reader
- Python 3.6+
- Administrator/root privileges for service installation

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/acr122u-keyboard-emulator.git
cd acr122u-keyboard-emulator

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Installing as a Service

#### Windows

Run the following command as Administrator:

```
scripts\install_service.bat
```

#### Linux

```bash
sudo ./scripts/install_service.sh
```

### Configuration

Edit the `config.json` file to customize behavior:

```json
{
  "prefix": "",
  "suffix": "\n",
  "log_level": "INFO",
  "format": "HEX"
}
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `prefix` | Text to type before the UID | `""` |
| `suffix` | Text to type after the UID | `"\n"` |
| `log_level` | Logging level (DEBUG, INFO, WARNING, ERROR) | `"INFO"` |
| `format` | Output format: HEX, DEC, or CUSTOM | `"HEX"` |

## How It Works

This emulator uses an optimized approach with card monitoring to detect NFC cards instantly:

1. **Card Monitoring**: Uses the PC/SC card monitoring system to receive events when cards are presented
2. **Direct USB Communication**: Falls back to direct USB for systems where PC/SC monitoring isn't available
3. **Keyboard Emulation**: Converts card UIDs to keyboard input with configurable formatting

## Troubleshooting

### Reader Not Found

1. Ensure the ACR122U is properly connected
2. Install the official drivers from [ACS](https://www.acs.com.hk/en/driver/3/acr122u-usb-nfc-reader/)
3. Make sure the PC/SC service is running
4. Try a different USB port

### Card Not Detected

1. Make sure you're using compatible Mifare cards
2. Try placing the card directly on the center of the reader
3. Check if the card works with other NFC applications

## Advanced Usage

### Running in Debug Mode

For detailed logging:

```bash
python main.py --debug
```

### Custom Card Formats

By default, the emulator outputs UIDs in hexadecimal format. For decimal or custom formats, modify the `format` option in config.json.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```