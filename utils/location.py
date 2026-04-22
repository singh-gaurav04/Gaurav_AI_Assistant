import requests

def get_location(ip):
    try:
        res = requests.get(f"https://ipapi.co/{ip}/json/")
        data = res.json()

        city = data.get("city")
        country = data.get("country_name")

        if city and country:
            return f"{city}, {country}"
        return "Unknown"
    except:
        return "Unknown"