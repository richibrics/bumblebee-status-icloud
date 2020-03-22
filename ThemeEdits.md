# Add AwesomeFonts icons to iCloud widgets 

## Install
iCloud module for [BumbleBee-Status](https://github.com/tobi-wan-kenobi/bumblebee-status) bar is not an official module so you 
have to add these lines to the JSON file that you can find at `BUMBLEBEE_FOLDER/themes/icons/awesome-fonts.json`:
``` json
  "icloud": {
    "charging": {
      "suffix": ["", "", "", "", ""]
    },
    "discharging-10": { "suffix": ""},
    "discharging-25": { "suffix": ""},
    "discharging-50": { "suffix": ""},
    "discharging-80": { "suffix": "" },
    "discharging-100": { "suffix": ""},
    "iPhone": {"prefix": ""},
    "Watch": {"prefix": ""}
  },
```

