from pyicloud import PyiCloudService
import configparser
import os
import time
import threading
import bumblebee.input
import bumblebee.output
import bumblebee.engine

ICLOUD_LOGINS_FOLDER = "iCloudLogins/"
REFRESH_TIMER = 60  # Seconds

currentPath = os.path.realpath(__file__)
currentPath = currentPath[:currentPath.rfind('/')+1]

# Get config file
config = configparser.ConfigParser()
config.read(currentPath + "icloud.ini")

# Read credentials from config file
email = config['iCloud']['email']
password = config['iCloud']['password']

api = PyiCloudService(email, password, currentPath+ICLOUD_LOGINS_FOLDER)

devicesInfo = []
refreshing = False

def UpdateBattery():
    global api, devicesInfo, refreshing
    while(True):
        refreshing = True
        devicesInfo = []
        devices = api.devices
        for device in devices:
            status = device.status()
            deviceName = str(status['name'])
            devicePercentage = int(round(status['batteryLevel']*100))
            if(devicePercentage > 0):  # Cause iMacs have 0% battery in status
                devicesInfo.append(
                    {'name': deviceName, 'battery': devicePercentage})
        refreshing=False
        time.sleep(REFRESH_TIMER)


thread = threading.Thread(target=UpdateBattery)
thread.start()


class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        widgets = []
        super(Module, self).__init__(engine, config, widgets)
        # bumblebee.output.Widget(full_text=self.icloud)
        self._update_widgets(widgets)

    def update(self, widgets):
        self._update_widgets(widgets)

    def _update_widgets(self, widgets):
        if not refreshing: # Cause maybe i erase devices array while bar updates
            for widget in widgets:
                widget.set("visited", False)

            for device in devicesInfo:
                # Check if widget was already created
                widget = self.widget(device['name'])
                # If not, I create the widget for the new device with the name of the device, to help me find it later
                if not widget:
                    widget = bumblebee.output.Widget(name=device['name'])
                    widgets.append(widget)
                # I set properties to the widget
                widget.full_text(device['name'] + ": " +
                                str(device['battery'])+'%')
                widget.set("visited", True)

            # The widget I have not touched now are widget of devices that may be offline now then I remove them
            for widget in widgets:
                if widget.get("visited") is False:
                    widgets.remove(widget)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
