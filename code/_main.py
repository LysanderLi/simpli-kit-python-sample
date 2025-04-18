import utime
import dataCall
from usr.libs import Application
from usr.libs.logging import getLogger
from usr.extensions import (
    qth_client,
    gnss_service,
    lbs_service,
    sensor_service,
)
import vsim


logger = getLogger(__name__)


def create_app(name="SimpliKit", version="1.0.0", config_path="/usr/config.json"):
    _app = Application(name, version)
    _app.config.init(config_path)

    qth_client.init_app(_app)
    gnss_service.init_app(_app)
    lbs_service.init_app(_app)
    sensor_service.init_app(_app)

    return _app


if __name__ == "__main__":
    while True:
        lte = dataCall.getInfo(1, 0)
        if lte[2][0] == 1:
            logger.debug('lte network normal')
            break
        logger.debug('wait lte network normal...')
        utime.sleep(3)
    vsim.enable()
    if vsim.queryState()!= 1:
        print("flooding well network failure")
        vsim.enable()
    # dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0)  # 激活之前，应该先配置APN，这里配置第1路的APN
    # dataCall.activate(1)
    ret=dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0)
    ret2=dataCall.activate(1)
    while not ret and ret2:
        ret=dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0)  # 激活之前，应该先配置APN，这里配置第1路的APN
        ret2=dataCall.activate(1)
        if  ret and ret2:
            print("Net injection failure")
            break
                
    app = create_app()
    app.run()
