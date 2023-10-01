import subprocess
from datetime import datetime

def log(text):
    log_msg = datetime.now().strftime("[%d/%m/%Y %H:%M:%S] ") + text
    with open("data/launcher_log.txt", "a") as file:
        file.write(log_msg+"\n")

log("launching bot...")

try:
    subprocess.run(["python", "bot.py"], check=True)
except subprocess.CalledProcessError as e:
    log(f"An error occurred while running the script: {e}")
