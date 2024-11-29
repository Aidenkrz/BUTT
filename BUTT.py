import json
import time
import requests
import websocket

#  ██████╗ ██╗   ██╗██████╗ ██╗  ██╗███████╗    ██████╗    ██╗   ██╗████████╗████████╗
#  ██╔══██╗██║   ██║██╔══██╗██║ ██╔╝██╔════╝    ██╔══██╗   ██║   ██║╚══██╔══╝╚══██╔══╝
#  ██║  ██║██║   ██║██████╔╝█████╔╝ ███████╗    ██████╔╝   ██║   ██║   ██║      ██║   
#  ██║  ██║██║   ██║██╔══██╗██╔═██╗ ╚════██║    ██╔══██╗   ██║   ██║   ██║      ██║   
#  ██████╔╝╚██████╔╝██║  ██║██║  ██╗███████║    ██████╔╝██╗╚██████╔╝██╗██║██╗   ██║██╗
#  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚═╝ ╚═════╝ ╚═╝╚═╝╚═╝   ╚═╝╚═╝

# Manifest URL, ex. https://cdn.networkgamez.com/fork/goobstation/manifest
manifest_url = "nuh uh"
# SS14 Server IP/Domain, ex. http://noda.avesmaximus.eu:4099/
server_ip = "nuh uh"
# Ptero API Key, generate this from: https://pterodactyl.app/account/api (replace pterodactyl.app with your domain), ex. https://admin.networkgamez.com/account/api
api_key = "nuh uh"
# Ptero API URL, separate from your server IP. This is the same as your panel's URL not including /server/serverid. ex. https://admin.networkgamez.com/
api_url = "nuh uh"
# Ptero Server ID, will be in the URL of the control panel page, or can be found in the settings tab of the server. Only accepts the first 8 characters, ex. a5b954ae
server_id = "nuh uh"
# Timeout - When to shutdown the script. You're probably running this server on a CRON Tab, so it should be equal or less than or equal to how often this runs.
timeout = 3600
# Discord Webhook URL, if left empty it will not do anything.
discord_webhook = "nuh uh"
# Discord Message to send when the server updates, put your message in the string after "content":
discord_message = { "content": "My super cool server has updated!" }

def main():
    if not sanity_check():  # Did you actually fill out all the fields? Probably not.
        return

    # Check for updates before sending update signal to SS14 and starting WebSocket connection
    data = fetch_build_data(manifest_url)  # Get JSON from manifest URL
    builds = data["builds"]  # Get builds from JSON

    latest_build_id = max(builds.keys(), key=lambda k: builds[k]["time"])  # Find latest build via timestamp
    current_build_id = get_current_build()  # Get current from the server

    if not check_for_update(current_build_id, latest_build_id):  # Check if latest build has changed
        return  # If no new builds, exit

    # Fetch the watchdog token from the server configuration file
    watchdog_token = get_watchdog_token()
    if not watchdog_token:
        print("Failed to obtain watchdog token.")
        return
    print("Obtained watchdog token.")
    
    send_update(watchdog_token)  # Make the POST request telling the server to update

    ws_info = get_websocket_info() 
    if ws_info:
        token = ws_info["token"]
        socket_url = ws_info["socket"]
        print(f"Generated WebSocket token.")
        connect_to_websocket(socket_url, token)  # Connect to the WebSocket
    else:
        print("Failed to obtain WebSocket info.")
        exit()

def sanity_check():
    errors = []  # Make sure we actually filled everything out :)

    if not manifest_url:
        errors.append("Manifest URL is not set.")
    if not server_ip:
        errors.append("Base URL is not set.")
    if not api_key:
        errors.append("API key is not set.")
    if not api_url:
        errors.append("API base URL is not set.")
    if not server_id:
        errors.append("Server ID is not set.")

    if errors:
        print("Sanity check failed with the following errors:")
        for error in errors:
            print(f" - {error}")
        return False
    return True

def fetch_build_data(manifest_url):
    try:
        response = requests.get(manifest_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        print("Manifest unavailable.")
        exit()

def get_current_build():
    try:
        response = requests.get(server_ip + "info")
        response.raise_for_status()
        data = response.json()
        return data['build']['version']
    except requests.exceptions.RequestException:
        print("SS14 API unavailable, is the server running?")
        exit()

def check_for_update(current_build_id, latest_build_id):
    print(f"Current server build: {current_build_id}")
    print(f"Latest manifest build: {latest_build_id}")
    if current_build_id == latest_build_id:  # If build id matches latest build id, return.
        print("Server build is up-to-date.")
        return False
    print("Server build is outdated.")
    return True

def get_watchdog_token():
    file_url = f"{api_url}api/client/servers/{server_id}/files/contents?file=%2Fdatadir%2Fserver_config.toml"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()
        config_data = response.text
        for line in config_data.splitlines():
            if line.strip().startswith("token"):
                return line.split("=")[1].strip().strip('"')
    except requests.exceptions.RequestException as e:
        print("GET request failed:", e)
    return None

def send_update(watchdog_token):
    try:
        headers = {"WatchdogToken": watchdog_token}
        response = requests.post(server_ip + "update", headers=headers)  # Sends an API call to SS14 to notify players of update and restart after the current round ends
        response.raise_for_status()
        print("Notified server of update after round end.")
    except requests.exceptions.RequestException:
        print("SS14 API unavailable, is the server running?")
        exit()

def get_websocket_info():
    websocket_info_url = f"{api_url}api/client/servers/{server_id}/websocket"  # Once again more ptero weirdness, you have to call a different API to get a token for the websocket.
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(websocket_info_url, headers=headers)
        response.raise_for_status()
        ws_info = response.json()
        return ws_info["data"]
    except requests.exceptions.RequestException as e:
        print("GET request failed:", e)
    except json.JSONDecodeError as e:
        print("Failed to decode JSON response:", e)
    return None

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("event") == "status":  # We only care about status events here, the rest are useless
            args = data.get("args", [])
            cleaned_args = ", ".join(args)  # Just prettifying the output for console
            print(f"Server is currently {cleaned_args}.")
            if args == ["starting"]:  # Checking if status is starting...
                time.sleep(2)
                call_kill() # Ptero thinks the server crashed when SS14 shuts down and automatically restarts it, so we need to kill it.
                time.sleep(2)
                call_reinstall()  # Tell Ptero to run the reinstall script.
                time.sleep(10)
                call_start()
                call_discord_webhook() # Sends a message to discord that the server has updated.
                ws.close()
        elif data.get("event") == "token expiring":
            print("WebSocket token expiring soon. Generating a new token.")
            ws_info = get_websocket_info()
            if ws_info:
                token = ws_info["token"]
                on_open(ws, token)
        elif data.get("event") == "auth_error":
            print("WebSocket token rejected. Exiting.")
            exit()
    except json.JSONDecodeError as e:
        print("Failed to decode message:", e)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")

def on_open(ws, token):
    auth_message = json.dumps({
        "event": "auth",
        "args": [token]
    })

    ws.send(auth_message)  # Sends token after connection established to websocket, because for some reason ptero doesn't allow you to pass that while connecting??

def connect_to_websocket(socket_url, token):
    print(f"Connecting to WebSocket.")
    start_time = time.time()
    ws = websocket.WebSocketApp(socket_url,
                                on_message=lambda ws, msg: on_message(ws, msg) or check_runtime(start_time),
                                on_error=on_error,
                                on_close=on_close,
                                on_open=lambda ws: on_open(ws, token))
    ws.run_forever()

def call_kill():
    power_url = f"{api_url}api/client/servers/{server_id}/power"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "signal": "kill"
    }
    try:
        response = requests.post(power_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Kill request sent successfully.")
    except requests.exceptions.RequestException as e:
        print("Kill request failed:", e)

def call_start():
    power_url = f"{api_url}api/client/servers/{server_id}/power"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "signal": "start"
    }
    try:
        response = requests.post(power_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Start request sent successfully.")
    except requests.exceptions.RequestException as e:
        print("Start request failed:", e)

def call_reinstall():
    reinstall_url = f"{api_url}api/client/servers/{server_id}/settings/reinstall"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(reinstall_url, headers=headers)
        response.raise_for_status()
        print("Reinstall request sent successfully.")
    except requests.exceptions.RequestException as e:
        print("Reinstall request failed:", e)

def check_runtime(start_time):
    if time.time() - start_time > timeout:  # If script runs for more than an hour, exit
        print("Script has timedout. Exiting.")
        exit()

def call_discord_webhook():
    if discord_webhook:
        response = requests.post(discord_webhook, json=discord_message)
        if response.status_code == 204:
            print("Discord message sent successfully!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    main()
