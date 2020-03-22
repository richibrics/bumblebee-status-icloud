from pyicloud import PyiCloudService
import configparser
import os
import time
import threading
import bumblebee.input
import bumblebee.output
import bumblebee.engine

ICLOUD_LOGINS_FOLDER="iCloudLogins/"
REFRESH_TIMER=60 #Seconds

currentPath = os.path.realpath(__file__)
currentPath = currentPath[:currentPath.rfind('/')+1]

# Get config file
config = configparser.ConfigParser()
config.read(currentPath + "icloud.ini")

# Read credentials from config file
email = config['iCloud']['email']
password=config['iCloud']['password']

api = PyiCloudService(email, password,currentPath+ICLOUD_LOGINS_FOLDER)

devicesInfo=[]

def UpdateBattery():
    global api, devicesInfo
    while(True):
        devicesInfo=[]
        devices = api.devices
        for device in devices:
            status=device.status()
            deviceName= status['name']
            devicePercentage= int(round(status['batteryLevel']*100))
            if(devicePercentage>0): #Cause iMacs have 0% battery in status
                devicesInfo.append({'name':deviceName, 'battery':devicePercentage})
        time.sleep(REFRESH_TIMER)

thread = threading.Thread(target=UpdateBattery)
thread.start()

class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config,
            bumblebee.output.Widget(full_text=self.icloud)
        )

    def icloud(self,widget):
        #Parse devices info array and return the string
        string=''
        for device in devicesInfo:
            string=string + device['name'] + ": " + str(device['battery'])+'% '
        return string



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
