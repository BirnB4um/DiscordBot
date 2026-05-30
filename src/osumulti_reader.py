import os
import json
import time
import requests
from Logger import get_logger
import traceback
from datetime import datetime


logger = get_logger("osumulti")


class OsuMultiReader():
    
    
    def get_lobbies_as_text(self, search_filter:dict=None, char_limit:int=2000) -> str:
        
        data = self.get_latest_data(search_filter)
        
        if not data:
            return "No lobby data available."
        
        timestamp = data.get("timestamp", 0)
        if timestamp:
            try:
                timestamp = datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")
            except Exception as e:
                logger.error(f"Error parsing timestamp: {e}. {timestamp}")
                timestamp = "<Invalid Timestamp>"
        else:
            timestamp = "Unknown"
            
        message = f"**MULTIPLAYER LOBBIES** (Last Updated: {timestamp})\n\n"
        
        for lobby in data.get("lobbies", []):
            
            lobby_name = lobby.get("name", "Unknown Lobby")
            message += f"- {lobby_name}\n"
            
            diff_range = lobby.get("difficulty_range", {})
            stars_str = f"★ {round(diff_range.get('min', 0), 1)} - {round(diff_range.get('max', 0), 1)}"
            
            players = lobby.get("recent_participants", [])
            player_flags = [f":flag_{p.get('country_code', '').lower()}:" for p in players if p.get("country_code")]
            players_str = f"{len(players)} player(s)"
            if player_flags:
                players_str += " " + " ".join(player_flags)
            
            message += f"`{stars_str}` | {players_str}\n\n"

        if len(message) > char_limit:
            message = message[:char_limit - 16] + "\n...(truncated)"

        return message
    
        
    def get_latest_data(self, search_filter:dict=None):
        try:
            if search_filter:
                response = requests.post("http://host.docker.internal:5001/api/osumulti/filter_latest_lobbies", json=search_filter)
            else:
                response = requests.get("http://host.docker.internal:5001/api/osumulti/latest_lobbies")
            if response.status_code != 200:
                return None
        
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching latest lobby data: {e}")
            logger.error(traceback.format_exc())
            return None