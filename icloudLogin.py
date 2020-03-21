from pyicloud import PyiCloudService
import configparser
import sys

ICLOUD_LOGINS_FOLDER = "iCloudLogins/"

# Get config file
config = configparser.ConfigParser()
config.read("icloud.ini")

# Read credentials from config file
email = config['iCloud']['email']
password = config['iCloud']['password']

api = PyiCloudService(email, password, ICLOUD_LOGINS_FOLDER)

if api.requires_2sa:
    print("Two-factor authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print(str(i) + ": " + str(device.get('deviceName',
                                             "SMS to" + str(device.get('phoneNumber')))))

    device = int(input('Which device would you like to use? '))
    device = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = int(input('Please enter validation code: '))
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

print("Connection success")
