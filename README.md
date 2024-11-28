# Durk's Bad Update Tracking Tool 

REQUIREMENTS: Python (duh) and `json, time, requests, websocket` pip packages, i think there is two websocket packages available, if one doesnt work get the other IG i dont remember which one to use
You also need to set a watchdog token in your server_config.toml, like this
```
[watchdog]
token = "supercoolandsecuretoken"
```
It really doesnt matter what you set it too, since we just grab it thru ptero anyways

You can run this script manually, but its kinda built for you to throw it on a CRON tab

## License
All code for the content repository is licensed under [PSPL](https://github.com/Aidenkrz/BUTT?tab=License-1-ov-file).
