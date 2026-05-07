import subprocess
from Logger import get_logger

logger = get_logger("launcher")

while True:
    logger.info("Launching bot...")
    result = subprocess.run(["python3", "bot.py"], capture_output=True, text=True)
    if result.returncode == 0:
        logger.info("Bot exited successfully.")
    else:
        logger.error(f"Bot exited with return code {result.returncode}.\nError output: {result.stderr}")
        break
        
