import os
import json
import time
import requests
from Logger import get_logger
import traceback
from datetime import datetime


logger = get_logger("osumulti")


class OsuMultiReader():
    
    def _parse_filter(self, search_filter:str):
        if not search_filter:
            return None
        
        search_filter = search_filter.strip()
        return search_filter

    
    def get_lobbies_as_text(self, search_filter:str=None, char_limit:int=2000) -> str:
        data = self.get_latest_data()
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
            if lobby.get("has_password"):
                continue
            
            lobby_name = lobby.get("name", "Unknown Lobby")
            message += f"- {lobby_name}\n"
            
            lobby_id = lobby.get("id", "N/A")
            id_str = f"ID: {lobby_id}"
            
            
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
    
    
    def _format_lobby_data(self, lobby_data:dict):
        return lobby_data
        
        
    def get_latest_data(self):
        try:
            response = requests.get("http://host.docker.internal:5001/api/osumulti/latest_lobbies")
            if response.status_code != 200:
                return None
        
            data = response.json()
            data["lobbies"] = [self._format_lobby_data(lobby) for lobby in data["lobbies"]]
            return data

        except Exception as e:
            logger.error(f"Error fetching latest lobby data: {e}")
            logger.error(traceback.format_exc())
            return None