import utime
import dataCall
from usr.libs import Application
from usr.libs.logging import getLogger
from usr.extensions import (
    qth_client,
    gnss_service,
    lbs_service,
    sensor_service,
    fan_service,
    buzzer_service,
)
 


logger = getLogger(__name__)


def create_app(name="SimpliKit", version="1.0.0", config_path="/usr/config.json"):
    _app = Application(name, version)
    _app.config.init(config_path)

    # If SIM service is available, try to register it with the application
    try:
        from usr.extensions import sim_service
        sim_service.init_app(_app)
    except ImportError:
        logger.debug("SIM service not available, skipping registration")
    
    qth_client.init_app(_app)
    gnss_service.init_app(_app)
    lbs_service.init_app(_app)
    sensor_service.init_app(_app)
    fan_service.init_app(_app)
    buzzer_service.init_app(_app)

    return _app


if __name__ == "__main__":
    # Try to import SIM service, use manual detection method if it fails
    try:
        from usr.extensions.sim_service import SIMService
        sim_svc = SIMService()
        if sim_svc.initialize_sim():
            sim_info = sim_svc.get_sim_info()
            logger.info("Using {} SIM card".format(sim_info['type']))
        else:
            logger.error("SIM card initialization failed, using manual detection")
            raise ImportError("SIM service failed")
    except ImportError:
        # If SIM service is not available, manual detection: prioritize physical SIM, fallback to vSIM
        logger.info("SIM service not available, manual SIM card detection...")
        import sim
        from sim import vsim
        
        # First ensure vSIM is disabled, then detect physical SIM
        try:
            vsim.disable()
            utime.sleep(2)
        except:
            pass
            
        # Detect physical SIM card
        sim_status = sim.getStatus()
        logger.info("Physical SIM card status: {}".format(sim_status))
        
        if sim_status == 1:
            # Physical SIM card available
            logger.info("Physical SIM card detected, using physical SIM")
        else:
            # Physical SIM not available, trying vSIM
            logger.info("Physical SIM card not available, trying vSIM")
            vsim.enable()
            while True:
                if vsim.queryState() == 1:
                    logger.info("vSIM enabled successfully")
                    break           
                vsim.enable()
                utime.sleep(2)
                logger.debug("Waiting for vSIM to enable...")

    # Configure data connection
    ret = dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0)
    ret2 = dataCall.activate(1)
    
    while ret and ret2:
        ret = dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0)
        ret2 = dataCall.activate(1)
        if not ret and not ret2:
            logger.info("Network connection successful")
            break
        logger.debug("Waiting for network connection...")
        utime.sleep(2)
        
    # Wait for LTE network to be ready
    while True:
        lte = dataCall.getInfo(1, 0)
        if lte[2][0] == 1:
            logger.debug('LTE network normal')
            break
        logger.debug('Waiting for LTE network to be normal...')
        utime.sleep(3)
            
    # Create and run application after network is ready
    app = create_app()
    app.run()
