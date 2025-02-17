import os
from plyer import notification

notif_file = os.path.join(os.getenv("TEMP"), "config", "notif.txt")

if os.path.exists(notif_file):
    with open(notif_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    titre = "Notification"
    message = "Aucun message trouvé."

    for line in lines:
        if line.startswith("titre ="):
            titre = line.split("=", 1)[1].strip()
        elif line.startswith("message ="):
            message = line.split("=", 1)[1].strip()

    notification.notify(title=titre, message=message, timeout=10)
