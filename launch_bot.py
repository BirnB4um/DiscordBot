import subprocess
from datetime import datetime

def log(text):
    log_msg = datetime.now().strftime("[%d/%m/%Y %H:%M:%S] ") + text
    with open("data/launcher_log.txt", "a") as file:
        file.write(log_msg+"\n")

log("launching bot...")

output = subprocess.run(["python", "bot.py"])
log(f"{output.stdout}\n{output.stderr}")
