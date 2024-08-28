from waybackpy import WaybackMachineCDXServerAPI
from waybackpy.exceptions import NoCDXRecordFound
from bs4 import BeautifulSoup
import requests
from typing import Literal

def get_archived_data(url, snapshotDate: Literal["oldest", "newest"] = "oldest"):   

    if snapshotDate not in ("oldest", "newest"):
        raise ValueError("Parameter 'snapshotDate' must be either 'oldest' or 'newest'.")
    
    try:
        user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
        cdx_api = WaybackMachineCDXServerAPI(url, user_agent)
        if snapshotDate == "newest":
            snapshot = cdx_api.newest()
        elif snapshotDate == "oldest":
            snapshot = cdx_api.oldest()
        else:
            return {"success": False, "error": "Invalid snapshot date"}
        
        date = snapshot.datetime_timestamp.strftime("%d.%m.%Y %H:%M:%S")

        response = requests.get(snapshot.archive_url, headers={"User-Agent": user_agent})

        if response.status_code != 200:
            return {"success": False, "error": f"status code {response.status_code} when fetching data"}
        
        type = response.headers['Content-Type']

        # if image, return directly
        if "image" in type:
            return {"success": True, "type": type, "date": date, "url": snapshot.archive_url, "content": response.content}
        
        # search for image in the page
        soup = BeautifulSoup(response.text, 'html.parser')
        iframe = soup.find('iframe', id="playback")
        if iframe:
            src = iframe.get('src')
            return {"success": True, "type": type, "date": date, "url": src}
        
        # if contains other data, return the url
        return {"success": True, "type": type, "date": date, "url": snapshot.archive_url}

    except NoCDXRecordFound:
        return {"success": False, "error": "No CDX record found"}
    except Exception as e:
        return {"success": False, "error": str(e)}