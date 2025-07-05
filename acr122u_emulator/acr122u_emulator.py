import time
import logging
import keyboard
import usb

try:
    from smartcard.System import readers
    from smartcard.Exceptions import CardConnectionException, NoCardException
    from smartcard.CardMonitoring import CardMonitor, CardObserver
    HAVE_PYSCARD = True
except ImportError:
    HAVE_PYSCARD = False
    print("Warning: pyscard not installed. Using direct USB communication only.")

class CardReaderObserver(CardObserver):
    """Card observer that detects card insertion/removal events"""
    
    def __init__(self, emulator):
        self.emulator = emulator
        super().__init__()
        
    def update(self, observable, actions):
        (added_cards, removed_cards) = actions
        
        for card in added_cards:
            self.emulator.logger.debug(f"Card inserted: {card}")
            uid = self.emulator.read_specific_card(card)
            if uid:
                self.emulator.type_uid(uid)
                
        for card in removed_cards:
            self.emulator.logger.debug(f"Card removed: {card}")
            self.emulator.last_uid = None

class ACR122UKeyboardEmulator:
    # APDU Commands
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    
    def __init__(self, prefix="", suffix="\n", log_level=logging.INFO):
        """
        Initialize the ACR122U Keyboard Emulator
        
        Args:
            prefix (str): Text to type before the UID
            suffix (str): Text to type after the UID (default: newline)
            log_level: Logging level
        """
        self.connection = None
        self.ep_in = None
        self.ep_out = None
        self.usb_dev = None
        self.prefix = prefix
        self.suffix = suffix
        self.last_uid = None
        self.reader = None
        
        # Setup logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ACR122U_Emulator")
        
    # Add this function to your ACR122UKeyboardEmulator class in acr122u_emulator.py
    def list_all_readers(self):
        """List all available smart card readers"""
        from smartcard.System import readers
        available_readers = readers()
        
        if not available_readers:
            self.logger.error("No smart card readers found on the system")
            return
            
        self.logger.info(f"Found {len(available_readers)} reader(s):")
        for i, reader in enumerate(available_readers):
            self.logger.info(f"  {i+1}. {reader.name}")

    def find_reader(self):
        """Find and connect to the ACR122U reader"""
        if not HAVE_PYSCARD:
            # Skip PC/SC detection and use direct USB only
            return self.setup_direct_usb()
        available_readers = readers()
        
        # List all readers for debugging
        self.list_all_readers()
        
        if not available_readers:
            self.logger.error("No smart card readers found")
            return False
        
        # Common names for ACR122U
        acr122u_names = ["ACR122U", "ACS ACR122", "ACS Reader"]
        
        for reader in available_readers:
            for name in acr122u_names:
                if name in reader.name:
                    self.reader = reader
                    self.logger.info(f"Found ACR122U reader: {reader.name}")
                    return True
                    
        self.logger.error("ACR122U reader not found")
        return False
    
    def setup_direct_usb(self):
        """Set up direct USB communication with the ACR122U"""
        try:
            import usb.core
            import usb.util
            
            # ACR122U vendor and product IDs
            VENDOR_ID = 0x072f
            PRODUCT_ID = 0x2200
            
            # Find the device
            self.usb_dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
            
            if self.usb_dev is None:
                self.logger.error("ACR122U not found via USB")
                return False
                
            # Set configuration
            if self.usb_dev.is_kernel_driver_active(0):
                self.usb_dev.detach_kernel_driver(0)
            self.usb_dev.set_configuration()
            
            # Get endpoints
            cfg = self.usb_dev.get_active_configuration()
            intf = cfg[(0,0)]
            
            self.ep_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            
            self.ep_in = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
            
            self.logger.info("Direct USB communication set up successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up direct USB: {e}")
            return False

    def read_card_uid_usb(self):
        """Read card UID using direct USB communication"""
        if not hasattr(self, 'usb_dev') or not hasattr(self, 'ep_out') or not hasattr(self, 'ep_in'):
            if not self.setup_direct_usb():
                return None
        
        try:
            # Command to get UID (direct protocol)
            command = [0xD4, 0x4A, 0x01, 0x00]
            packet = [0xFF, 0x00, 0x00, 0x00, len(command)] + command
            
            # Send command
            self.ep_out.write(packet)
            
            # Read response (with timeout)
            try:
                response = self.ep_in.read(256, timeout=100)
                
                if len(response) > 2 and response[0] == 0xD5 and response[1] == 0x4B:
                    uid_length = response[2]
                    uid = response[3:3+uid_length]
                    uid_hex = ''.join(f'{x:02X}' for x in uid)
                    return uid_hex
            except usb.core.USBError:
                # Timeout or no card present - expected behavior
                pass
                
            return None
                
        except Exception as e:
            self.logger.error(f"Error in direct USB communication: {e}")
            # Reset USB connection on error
            self.usb_dev = None
            self.ep_out = None
            self.ep_in = None
            return None
    
    def read_card_uid(self):
        """Read the UID from a Mifare card with optimized performance"""
        if not self.reader:
            return None
            
        try:
            # Create connection only once and reuse it
            if not hasattr(self, 'connection') or self.connection is None:
                self.connection = self.reader.createConnection()
                
            # Try to connect (will fail if no card present, which is expected)
            try:
                self.connection.connect()
            except NoCardException:
                return None
                
            # Send command to get UID
            response, sw1, sw2 = self.connection.transmit(self.GET_UID)
            
            if sw1 == 0x90 and sw2 == 0x00:
                uid = ''.join(f'{x:02X}' for x in response)
                return uid
            else:
                self.logger.warning(f"Failed to read card: SW1={sw1:02X}, SW2={sw2:02X}")
                return None
                    
        except CardConnectionException:
            # Reset connection on error
            self.connection = None
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.connection = None
            return None
    
    def type_uid(self, uid):
        """Type the UID as keyboard input"""
        if uid:
            full_text = f"{self.prefix}{uid}{self.suffix}"
            self.logger.info(f"Typing: {full_text.strip()}")
            keyboard.write(full_text)

    def read_specific_card(self, card):
        """Read UID from a specific card"""
        try:
            connection = card.createConnection()
            connection.connect()

            response, sw1, sw2 = connection.transmit(self.GET_UID)

            if sw1 == 0x90 and sw2 == 0x00:
                uid = ''.join(f'{x:02X}' for x in response)
                return uid
            else:
                return None
        except Exception:
            return None
        
    def run(self):
        """Main loop to read cards and emulate keyboard using card monitoring"""
        if not self.find_reader():
            return
                
        self.logger.info("Starting card monitoring. Press Ctrl+C to exit.")
        
        try:
            self.cardmonitor = CardMonitor()
            self.cardobserver = CardReaderObserver(self)
            self.cardmonitor.addObserver(self.cardobserver)
            
            while True:
                time.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("Exiting...")
            if hasattr(self, 'cardmonitor') and hasattr(self, 'cardobserver'):
                self.cardmonitor.deleteObserver(self.cardobserver)
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            if hasattr(self, 'cardmonitor') and hasattr(self, 'cardobserver'):
                self.cardmonitor.deleteObserver(self.cardobserver)