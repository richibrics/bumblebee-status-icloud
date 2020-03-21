from pyicloud import PyiCloudService
import configparser
import bumblebee.input
import bumblebee.output
import bumblebee.engine

ICLOUD_LOGINS_FOLDER="iCloudLogins/"

# Get config file
config = configparser.ConfigParser()
config.read("icloud.ini")

# Read credentials from config file
email = config['iCloud']['email']
password=config['iCloud']['password']

api = PyiCloudService(email, password,'ICLOUD_LOGINS_FOLDER)

class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config,
            bumblebee.output.Widget(full_text=self.icloud)
        )
        self._info=""
        

    def icloud(self,widget):
        return self._info
    
    def update(self, widget):
        device=api.devices[0]
        status=device.status()
        self._info=status['deviceDisplayName']+ ": " + str(round(status['batteryLevel']*100))+'%'

    def state(self, widget):
        return True

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
