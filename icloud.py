"""
Requires the following python module:
    * pyicloud
Parameters:
    * nic.exclude: Comma-separated list of interface prefixes to exclude (defaults to "lo,virbr,docker,vboxnet,veth,br")
    * nic.include: Comma-separated list of interfaces to include
    * nic.states: Comma-separated list of states to show (prefix with "^" to invert - i.e. ^down -> show all devices that are not in state down)
    * nic.format: Format string (defaults to "{intf} {state} {ip} {ssid}")
"""
import arrow 

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
DISPLAY_PROPERTY= 'modelDisplayName'

currentPath = os.path.realpath(__file__)
currentPath = currentPath[:currentPath.rfind('/')+1]

# Get config file
config = configparser.ConfigParser()
config.read(currentPath + "icloud.ini")

# Read credentials from config file
email = config['iCloud']['email']
password = config['iCloud']['password']

devicesInfo = []
refreshing = False

def Log(message):
    current_time = arrow.utcnow().format('YYYY-MM-DD HH:mm:ss')
    line=current_time+" | " +message+'\n'
    f = open(currentPath+"log.txt", "a")
    f.write(line)
    f.close()

def UpdateBattery():
    Log("Thread started")
    global  devicesInfo, refreshing
    api = PyiCloudService(email, password, currentPath+ICLOUD_LOGINS_FOLDER)
    while(True):
        refreshing = True
        Log("Refreshing")
        Log(str(api))
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
        Log(str(devicesInfo))
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
        self._exclude = tuple(filter(len, self.parameter("exclude", "imac").split(",")))
        Log("Init module")

    def _update_widgets(self, widgets):
        if not refreshing: # Cause maybe i erase devices array while bar updates
            # Removes devices to exclude
            devicesInfoToAdd = [d for d in devicesInfo if not d['name'].startswith(self._exclude)]
            for widget in widgets:
                widget.set("visited", False)

            for device in devicesInfoToAdd:
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
                widget.set("charging", device['charging'])
                widget.set("class", device['class'])
                widget.set("battery", device['battery'])

            # The widget I have not touched now are widget of devices that may be offline now then I remove them
            for widget in widgets:
                if widget.get("visited") is False:
                    widgets.remove(widget)

    def update(self, widgets):
        global thread
        if(not thread.is_alive()):
            Log("Thread was not running: starting...")
            thread = threading.Thread(target=UpdateBattery)
            thread.start()
        self._update_widgets(widgets)

    def state(self, widget):
        states = []

        if widget.get("charging"):
            states.append("charging")
        else:
            state="discharging-"
            if(widget.get("battery")<=10):
                states.append("critical")
                state=state+'10'
            elif(widget.get("battery")<=25):
                state=state+'25'
                states.append("warning")
            elif(widget.get("battery")<=50):
                state=state+'50'
            elif(widget.get("battery")<=80):
                state=state+'80'
            else:
                state=state+'100'
            states.append(state)

        states.append(widget.get("class"))
        return states


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
