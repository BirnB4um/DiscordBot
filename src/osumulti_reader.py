import os
import json
import time
import requests
from Logger import get_logger
import traceback
from datetime import datetime


logger = get_logger("osumulti")


class OsuMultiReader():
    
    
    def parse_filters(self, filter_str:str):
        
        
        search_filter = {
            "public": True,  # default to only public lobbies
        }
        
        filter_str = filter_str or ""
        if not filter_str.strip():
            return True, search_filter
        
        for filter in filter_str.split(";"):
            
            filter = filter.strip()
            if not filter or ":" not in filter:
                return False, f"invalid filter format: `{filter}`. Use key:value pairs separated by semicolons."
            
            command_split = filter.split(":")
            if len(command_split) != 2:
                return False, f"invalid filter format: `{filter}`. Use key:value pairs separated by semicolons."
            
            key, value = command_split[0], command_split[1]
            key = key.strip().lower()
            value = value.strip().lower()
            
            if key == "country":
                search_filter["country"] = [c.strip().lower() for c in value.split(",") if c.strip()]
                
            elif key == "public":
                if value == "all":
                    del search_filter["public"]
                    continue
                search_filter["public"] = value in ["true", "1", "yes"]
                
            elif key == "diff":
                if "-" in value:
                    min_diff, max_diff = value.split("-", 1)
                    try:
                        search_filter["diff"] = [float(min_diff.strip()), float(max_diff.strip())]
                    except ValueError:
                        return False, "invalid diff format. Use min-max (e.g. diff:2.1-4.5 OR diff:3.5)"
                else:
                    try:
                        diff = float(value)
                        search_filter["diff"] = [diff, diff]
                    except ValueError:
                        return False, "invalid diff format. Use min-max (e.g. diff:2.1-4.5 OR diff:3.5)"

            elif key == "player":
                if "-" in value:
                    min_player, max_player = value.split("-", 1)
                    try:
                        search_filter["player"] = [int(min_player.strip()), int(max_player.strip())]
                    except ValueError:
                        return False, "invalid player format. Use min-max (e.g. player:1-5 OR player:3)"
                else:
                    try:
                        player = int(value)
                        search_filter["player"] = [player, player]
                    except ValueError:
                        return False, "invalid player format. Use min-max (e.g. player:1-5 OR player:3)"

            elif key == "limit":
                try:
                    search_filter["limit"] = int(value)
                except ValueError:
                    return False, "invalid limit format. Use an integer > 0 (e.g. limit:10)"
                
            else:
                return False, f"unknown filter key: {key}. Use .osu_lobbies help for filter options."

        return True, search_filter


    
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
            stars_str = f"★ {round(diff_range.get('min', 0), 1)} - {round(diff_range.get('max', 0), 1)}" # ⬤
            
            players = lobby.get("recent_participants", [])
            player_flags = [f":flag_{p.get('country_code', '').lower()}:" for p in players if p.get("country_code")]
            players_str = f"{len(players)} player(s)"
            if player_flags:
                players_str += " " + " ".join(player_flags)
            
            if lobby.get("has_password", False):
                message += "🔒 "
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