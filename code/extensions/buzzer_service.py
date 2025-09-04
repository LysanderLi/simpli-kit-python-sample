import utime
from usr.libs.threading import Thread, Lock
from usr.libs.logging import getLogger
from usr.libs import CurrentApp

logger = getLogger(__name__)

try:
    from machine import Pin
    GPIO_AVAILABLE = True
except ImportError:
    logger.warn("GPIO (machine.Pin) not available, buzzer control will be simulated")
    GPIO_AVAILABLE = False


class BuzzerService(object):
    """Buzzer control service for managing buzzer switch with hot-plug support"""

    def __init__(self, app=None):
        self.buzzer_lock = Lock()
        self.buzzer_switch = False  # Buzzer on/off state
        self.buzzer_pin = None     # GPIO pin controller
        self.gpio_available = GPIO_AVAILABLE
        self.buzzer_hardware_available = False  # Track buzzer hardware availability
        
        # Buzzer GPIO configuration (GPIO36 as per buzzer.py)
        self.BUZZER_PIN = None
        if GPIO_AVAILABLE:
            try:
                # Try to get GPIO36 pin number safely
                self.BUZZER_PIN = getattr(Pin, 'GPIO36', None)
                if self.BUZZER_PIN is None:
                    # Fallback to other common pins
                    self.BUZZER_PIN = getattr(Pin, 'GPIO1', None) or getattr(Pin, 'GPIO2', None)
            except Exception as e:
                self.gpio_available = False
        
        # Initialize GPIO if available
        self._init_buzzer_gpio()
        
        if app is not None:
            self.init_app(app)

    def _init_buzzer_gpio(self):
        """Initialize GPIO controller for buzzer control with hot-plug support"""
        if not self.gpio_available or self.BUZZER_PIN is None:
            logger.info("GPIO not available, buzzer control will be simulated")
            self.buzzer_hardware_available = False
            return
            
        try:
            # Initialize GPIO pin: output mode, pull disabled, initial low level
            self.buzzer_pin = Pin(self.BUZZER_PIN, Pin.OUT, Pin.PULL_DISABLE, 0)
            self.buzzer_pin.init()
            self.buzzer_hardware_available = True
            logger.info("Buzzer GPIO initialized successfully on pin {}".format(self.BUZZER_PIN))
        except Exception as e:
            self.buzzer_pin = None
            self.buzzer_hardware_available = False

    def _try_reconnect_buzzer(self):
        """Attempt to reconnect buzzer hardware"""
        if self.buzzer_hardware_available:
            return True  # Already connected
            
        if not self.gpio_available or self.BUZZER_PIN is None:
            return False  # GPIO not available
            
        try:
            # Try to reinitialize GPIO
            self.buzzer_pin = Pin(self.BUZZER_PIN, Pin.OUT, Pin.PULL_DISABLE, 0)
            self.buzzer_pin.init()
            self.buzzer_hardware_available = True
            logger.info("Buzzer hardware reconnected successfully")
            
            # Apply current buzzer state
            self._apply_buzzer_state()
            
            return True
        except Exception as e:
            self.buzzer_pin = None
            self.buzzer_hardware_available = False
            return False

    def _mark_buzzer_disconnected(self):
        """Mark buzzer as disconnected when operation fails"""
        if self.buzzer_hardware_available:
            self.buzzer_hardware_available = False
            self.buzzer_pin = None

    def __str__(self):
        return '{}'.format(type(self).__name__)

    def init_app(self, app):
        """Register buzzer service with application"""
        app.register('buzzer_service', self)

    def load(self):
        """Load buzzer service - called by application framework"""
        logger.info('Loading {} extension'.format(self))
        # Start status reporting thread
        Thread(target=self._status_reporting_loop).start()

    def set_buzzer_switch(self, switch_on):
        """
        Control buzzer switch with hot-plug support
        Args:
            switch_on (bool): True to turn on buzzer, False to turn off
        Returns:
            bool: True if operation successful
        """
        with self.buzzer_lock:
            try:
                self.buzzer_switch = bool(switch_on)
                
                # Try to reconnect if hardware is not available
                if not self.buzzer_hardware_available:
                    self._try_reconnect_buzzer()
                    
                success = self._apply_buzzer_state()
                if success:
                    logger.info("Buzzer turned {}".format("ON" if self.buzzer_switch else "OFF"))
                else:
                    pass  # Silent when hardware not available
                return success
                
            except Exception as e:
                logger.error("Failed to set buzzer switch: {}".format(e))
                self._mark_buzzer_disconnected()
                return False

    def get_buzzer_status(self):
        """
        Get current buzzer status
        Returns:
            dict: {'switch': bool, 'hardware_available': bool}
        """
        with self.buzzer_lock:
            return {
                'switch': self.buzzer_switch,
                'hardware_available': self.buzzer_hardware_available
            }

    def _apply_buzzer_state(self):
        """Apply current buzzer state to GPIO controller with hot-plug support"""
        if not self.gpio_available:
            return True  # Simulate success when GPIO not available
            
        if not self.buzzer_hardware_available or not self.buzzer_pin:
            return False  # Hardware not available
            
        try:
            # Apply buzzer state: 1 for ON, 0 for OFF
            gpio_value = 1 if self.buzzer_switch else 0
            self.buzzer_pin.write(gpio_value)
            return True
        except Exception as e:
            self._mark_buzzer_disconnected()
            return False

    def _status_reporting_loop(self):
        """Background thread for periodic status reporting and reconnection"""
        reconnect_counter = 0
        
        while True:
            try:
                # Try to reconnect buzzer hardware every 30 seconds
                if reconnect_counter % 30 == 0:
                    if not self.buzzer_hardware_available:
                        self._try_reconnect_buzzer()
                
                # Report status every 60 seconds
                if reconnect_counter % 60 == 0:
                    if CurrentApp().qth_client.isStatusOk():
                        self._report_status()
                    
            except Exception as e:
                pass
            
            reconnect_counter += 1
            utime.sleep(2)  # Check every 2 seconds

    def _report_status(self):
        """Report current buzzer status to IoT platform"""
        try:
            status = self.get_buzzer_status()
            data = {
                13: status['switch']  # Buzzer switch (TSL ID 13)
            }
            
            with CurrentApp().qth_client:
                CurrentApp().qth_client.sendTsl(1, data)
                    
        except Exception as e:
            pass