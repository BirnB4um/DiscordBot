import subprocess
from datetime import datetime

def log(text):
    log_msg = datetime.now().strftime("[%d/%m/%Y %H:%M:%S] ") + text
    with open("data/launcher_log.txt", "a") as file:
        file.write(log_msg+"\n")


log("launching bot...")
process = subprocess.Popen(["python", "bot.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for line in process.stdout:
    with open("data/launcher_log.txt", "a") as logfile:
        logfile.write(line)

process.wait()
