from usr import Qth
import _thread
import dataCall
import utime
import log
from machine import Pin  # Import GPIO control module

logApp = log.getLogger("examp")

# Initialize buzzer control pin (assuming BZZ pin is connected to GPIO1)
BUZZER_PIN = Pin.GPIO36
buzzer = Pin(BUZZER_PIN, Pin.OUT, Pin.PULL_DISABLE, 0)  # Initial low level
buzzer.init()

def App_devEventCb(event, result):
    logApp.info('dev event:{} result:{}'.format(event, result))
    if event == 2 and result == 0:
        Qth.otaRequest()

def App_cmdRecvTransCb(value):
    ret = Qth.sendTrans(1, value)
    logApp.info('recvTrans value:{} ret:{}'.format(value, ret))

def App_cmdRecvTslCb(value):
    logApp.info('recvTsl:{}'.format(value))
    for cmdId, val in value.items():
        logApp.info('recvTsl {}:{}'.format(cmdId, val))
        # Add buzzer control handling (thing model ID=5)
        if cmdId == 5:
            control_buzzer(val)

def control_buzzer(state):
    """Control buzzer state"""
    if state:
        buzzer.write(1)  # High level
        logApp.info("BUZZER ON")
    else:
        buzzer.write(0)  # Low level
        logApp.info("BUZZER OFF")

def App_cmdReadTslCb(ids, pkgId):
    logApp.info('readTsl ids:{} pkgId:{}'.format(ids, pkgId))
    value = dict()
    for id in ids:
        if id == 1:
            value[1] = 180.25
        elif id == 2:
            value[2] = 30
        elif id == 3:
            value[3] = True
        # Add buzzer status reporting
        elif id == 5:
            value[5] = bool(buzzer.read())  # Read current state
    Qth.ackTsl(1, value, pkgId)

def App_cmdRecvTslServerCb(serverId, value, pkgId):
    logApp.info('recvTslServer serverId:{} value:{} pkgId:{}'.format(serverId, value, pkgId))
    Qth.ackTslServer(1, serverId, value, pkgId)

def App_otaPlanCb(plans):
    logApp.info('otaPlan:{}'.format(plans))
    Qth.otaAction(1)

def App_fotaResultCb(comp_no, result):
    logApp.info('fotaResult comp_no:{} result:{}'.format(comp_no, result))
    
def App_sotaInfoCb(comp_no, version, url, fileSize, md5, crc):
    logApp.info('sotaInfo comp_no:{} version:{} url:{} fileSize:{} md5:{} crc:{}'.format(
        comp_no, version, url, fileSize, md5, crc))
    Qth.setMcuVer('MCU1', 'V1.0.0', App_sotaInfoCb, App_sotaResultCb)

def App_sotaResultCb(comp_no, result):
    logApp.info('sotaResult comp_no:{} result:{}'.format(comp_no, result))

def Qth_tslSend():
    static_var = 0
    while True:
        if Qth.state():
            # Report data includes buzzer status (ID=5)
            Qth.sendTsl(1, {
                1: static_var,          # Original data
                5: bool(buzzer.read())  # Current buzzer status
            })
            static_var = (static_var + 1) % 100  # Prevent overflow
        utime.sleep(30)

if __name__ == '__main__':
    # Initialize network connection
    dataCall.setAutoActivate(1, 1)
    dataCall.setAutoConnect(1, 1)
    
    # Initialize Qth cloud platform
    Qth.init()
    Qth.setProductInfo('pe17Nb','SCttazY5WFZSblBX')
    
    # Set callback functions
    eventOtaCb = {
        'otaPlan': App_otaPlanCb,
        'fotaResult': App_fotaResultCb
    }
    eventCb = {
        'devEvent': App_devEventCb,
        'recvTrans': App_cmdRecvTransCb,
        'recvTsl': App_cmdRecvTslCb,
        'readTsl': App_cmdReadTslCb,
        'readTslServer': App_cmdRecvTslServerCb,
        'ota': eventOtaCb
    }
    Qth.setEventCb(eventCb)
    
    # Set version information
    Qth.setMcuVer('MCU1', 'V1.1', App_sotaInfoCb, App_sotaResultCb)
    Qth.setMcuVer('MCU2', 'V2.1', App_sotaInfoCb, App_sotaResultCb)
    
    # Start cloud platform connection
    Qth.start()
    
    # Start data reporting thread
    pid = _thread.start_new_thread(Qth_tslSend, ())
    logApp.info('Qth_tslSend thread:{} start'.format(pid))
    
    # Initialize buzzer state
    buzzer.write(0)  # Default off
    logApp.info("Buzzer initialized - READY")