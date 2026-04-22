import requests
from rich import print
import os 
from dotenv import load_dotenv

load_dotenv()

def get_location(ip:str):
    
    try:
        ip_arr = ip.split(",")
        for i in ip_arr:
            trimmed_ip = i.strip()
            api_key = os.getenv("IP_KEY")
            print(f"https://api.ipstack.com/{trimmed_ip}?access_key={api_key}")
            res = requests.get(f"https://api.ipstack.com/{trimmed_ip}?access_key={api_key}")
            data = res.json()
            city = data.get("city")
            country = data.get("country_name")
            region = data.get("region_name")
            if city and country:
                break
        return  f"{city},{region}, {country}"
    except:
        return "Unknown from expect"

