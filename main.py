import logging
from acr122u_emulator.config import Configuration
from acr122u_emulator.acr122u_emulator import ACR122UKeyboardEmulator

def main():
    # Load config
    config = Configuration()

    # Map string log level to logging constants
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    log_level = log_levels.get(config.get("log_level", "INFO"), logging.INFO)
    
    # Create emulator instance
    emulator = ACR122UKeyboardEmulator(
        prefix=config.get("prefix", ""),
        suffix=config.get("suffix", "\n"),
        log_level=log_level
    )

    # Run Emulator
    emulator.run()

if __name__ == "__main__":
    main()