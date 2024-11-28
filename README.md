# Durk's Bad Update Tracking Tool 

REQUIREMENTS: Python (duh), `requests`, and `websocket-client` pip packages, make SURE you install `websocket-client` and not `websocket`

You also need to set a watchdog token in your server_config.toml, like this
```
[watchdog]
token = "supercoolandsecuretoken"
```
It really doesnt matter what you set it too, since we just grab it thru ptero anyways

You can run this script manually, but its kinda built for you to throw it on a CRON tab

## License
All code for the content repository is licensed under [PSPL](https://github.com/Aidenkrz/BUTT?tab=License-1-ov-file).
