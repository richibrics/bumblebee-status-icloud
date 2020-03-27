from pyicloud import PyiCloudService
import configparser
import time

ICLOUD_LOGINS_FOLDER = "iCloudLogins/"
REFRESH_TIMER = 60  # Seconds
DISPLAY_PROPERTY= 'modelDisplayName'
config = configparser.ConfigParser()
config.read( "icloud.ini")

email = config['iCloud']['email']
password = config['iCloud']['password']

api = PyiCloudService(email, password, ICLOUD_LOGINS_FOLDER)
while(True):
    refreshing = True
    devicesInfo = []
    devices = api.devices
    for device in devices:
        info={}
        status = device.status(['deviceClass','batteryStatus',DISPLAY_PROPERTY]) # https://github.com/picklepete/pyicloud/issues/220
        info['name'] = str(status[DISPLAY_PROPERTY])
        info['battery'] = int(round(status['batteryLevel']*100))
        info['class']=str(device ['deviceClass'])
        if(device['batteryStatus']=="Charging"):
            info['charging']=True
        else:
            info['charging']=False
        if(info['battery'] > 0):  # Cause iMacs/offline devices have 0% battery in status
            devicesInfo.append(info)
    refreshing=False
    print(devicesInfo)
    time.sleep(REFRESH_TIMER)
