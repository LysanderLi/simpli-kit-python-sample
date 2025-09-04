import utime
from usr.libs.threading import Thread, Lock
from usr.libs.logging import getLogger
from usr.libs import CurrentApp

logger = getLogger(__name__)

try:
    from misc import PWM_V2
    PWM_AVAILABLE = True
except ImportError:
    logger.warn("PWM_V2 not available, fan control will be simulated")
    PWM_AVAILABLE = False


class FanService(object):
    """Fan control service for managing fan switch and speed modes"""

    def __init__(self, app=None):
        self.fan_lock = Lock()
        self.fan_switch = False  # Fan on/off state
        self.fan_mode = 1        # Fan speed mode (1=low, 2=medium, 3=high)
        self.pwm = None         # PWM controller
        self.pwm_available = PWM_AVAILABLE
        self.fan_hardware_available = False  # Track fan hardware availability
        
        # Initialize PWM with hot-plug support
        self._init_pwm()
        
        if app is not None:
            self.init_app(app)

    def _init_pwm(self):
        """Initialize PWM controller for fan control with hot-plug support"""
        if not self.pwm_available:
            logger.info("PWM not available, fan control will be simulated")
            self.fan_hardware_available = False
            return
            
        try:
            # Initialize PWM on PWM0 channel, 100Hz frequency, 0% initial duty cycle
            self.pwm = PWM_V2(PWM_V2.PWM0, 100.0, 0)
            self.fan_hardware_available = True
            logger.info("Fan PWM controller initialized successfully")
        except Exception as e:
            self.pwm = None
            self.fan_hardware_available = False

    def _try_reconnect_fan(self):
        """Attempt to reconnect fan hardware"""
        if self.fan_hardware_available:
            return True  # Already connected
            
        if not self.pwm_available:
            return False  # PWM module not available
            
        try:
            # Try to reinitialize PWM
            self.pwm = PWM_V2(PWM_V2.PWM0, 100.0, 0)
            self.fan_hardware_available = True
            logger.info("Fan hardware reconnected successfully")
            
            # If fan was supposed to be on, reapply settings
            if self.fan_switch:
                self._apply_fan_settings()
            
            return True
        except Exception as e:
            self.pwm = None
            self.fan_hardware_available = False
            return False

    def _mark_fan_disconnected(self):
        """Mark fan as disconnected when operation fails"""
        if self.fan_hardware_available:
            self.fan_hardware_available = False
            self.pwm = None

    def __str__(self):
        return '{}'.format(type(self).__name__)

    def init_app(self, app):
        """Register fan service with application"""
        app.register('fan_service', self)

    def load(self):
        """Load fan service - called by application framework"""
        logger.info('Loading {} extension'.format(self))
        # Start status reporting thread
        Thread(target=self._status_reporting_loop).start()

    def set_fan_switch(self, switch_on):
        """
        Control fan switch with hot-plug support
        Args:
            switch_on (bool): True to turn on fan, False to turn off
        Returns:
            bool: True if operation successful
        """
        with self.fan_lock:
            try:
                if switch_on:
                    self.fan_switch = True
                    # Try to reconnect if hardware is not available
                    if not self.fan_hardware_available:
                        self._try_reconnect_fan()
                        
                    success = self._apply_fan_settings()
                    if success:
                        logger.info("Fan turned ON with mode {} ({}% duty cycle)".format(
                            self.fan_mode, self._get_duty_cycle()))
                    else:
                        pass
                    return success
                else:
                    self.fan_switch = False
                    success = self._stop_fan()
                    if success:
                        logger.info("Fan turned OFF")
                    elif self.fan_hardware_available:
                        pass
                    return success
            except Exception as e:
                logger.error("Failed to set fan switch: {}".format(e))
                self._mark_fan_disconnected()
                return False

    def set_fan_mode(self, mode):
        """
        Set fan speed mode with hot-plug support
        Args:
            mode (int): Speed mode (1=low, 2=medium, 3=high)
        Returns:
            bool: True if operation successful
        """
        with self.fan_lock:
            try:
                if mode not in [1, 2, 3]:
                    logger.error("Invalid fan mode: {}. Must be 1, 2, or 3".format(mode))
                    return False
                
                self.fan_mode = mode
                
                # If fan is currently on, apply new settings
                if self.fan_switch:
                    # Try to reconnect if hardware is not available
                    if not self.fan_hardware_available:
                        self._try_reconnect_fan()
                        
                    success = self._apply_fan_settings()
                    if success:
                        logger.info("Fan mode updated to {} ({}% duty cycle)".format(
                            mode, self._get_duty_cycle()))
                    else:
                        pass
                    return success
                else:
                    logger.info("Fan mode set to {} (will apply when fan is turned on)".format(mode))
                    return True
                    
            except Exception as e:
                logger.error("Failed to set fan mode: {}".format(e))
                self._mark_fan_disconnected()
                return False

    def get_fan_status(self):
        """
        Get current fan status
        Returns:
            dict: {'switch': bool, 'mode': int, 'hardware_available': bool}
        """
        with self.fan_lock:
            return {
                'switch': self.fan_switch,
                'mode': self.fan_mode,
                'hardware_available': self.fan_hardware_available
            }

    def _get_duty_cycle(self):
        """Get PWM duty cycle percentage based on fan mode"""
        # Minimal power to prevent system restart due to power supply limitation
        # Mode 1: 10% (最低速), Mode 2: 18% (低速), Mode 3: 25% (中速)
        duty_cycles = {1: 10, 2: 18, 3: 25}
        return duty_cycles.get(self.fan_mode, 10)

    def _apply_fan_settings(self):
        """Apply current fan settings to PWM controller with hot-plug support"""
        if not self.pwm_available:
            logger.debug("PWM module not available, simulating fan control")
            return True
            
        if not self.fan_hardware_available or not self.pwm:
            logger.debug("Fan hardware not available, cannot apply settings")
            return False
            
        try:
            duty_cycle = self._get_duty_cycle()
            self.pwm.open(100.0, duty_cycle)
            return True
        except Exception as e:
            self._mark_fan_disconnected()
            return False

    def _stop_fan(self):
        """Stop fan by closing PWM with hot-plug support"""
        if not self.pwm_available:
            logger.debug("PWM module not available, simulating fan stop")
            return True
            
        if not self.fan_hardware_available or not self.pwm:
            logger.debug("Fan hardware not available, cannot stop fan")
            return False
            
        try:
            self.pwm.close()
            return True
        except Exception as e:
            self._mark_fan_disconnected()
            return False

    def _status_reporting_loop(self):
        """Background thread for periodic status reporting and reconnection"""
        reconnect_counter = 0
        
        while True:
            try:
                # Try to reconnect fan hardware every 30 seconds
                if reconnect_counter % 30 == 0:
                    if not self.fan_hardware_available:
                        self._try_reconnect_fan()
                
                # Report status every 60 seconds
                if reconnect_counter % 60 == 0:
                    if CurrentApp().qth_client.isStatusOk():
                        self._report_status()
                    
            except Exception as e:
                pass
            
            reconnect_counter += 1
            utime.sleep(2)  # Check every 2 seconds

    def _report_status(self):
        """Report current fan status to IoT platform"""
        try:
            status = self.get_fan_status()
            data = {
                11: status['switch'],  # Fan switch (TSL ID 11)
                12: status['mode']     # Fan mode (TSL ID 12)
            }
            
            with CurrentApp().qth_client:
                CurrentApp().qth_client.sendTsl(1, data)
                    
        except Exception as e:
            pass