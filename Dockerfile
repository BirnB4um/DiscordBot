FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Berlin

WORKDIR /opt/discord-bot
COPY requirements.txt .

RUN python -m pip install --upgrade pip \
&& python -m pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt/discord-bot/data/temp

COPY src /opt/discord-bot/src
COPY start.sh .
RUN chmod 755 start.sh

ENTRYPOINT ["./start.sh"]
