import requests

def get_location(ip):
    try:
        ip_arr = ip.split(",")
        city = ""
        region = ""
        country = ""

        for i in ip_arr:
            res = requests.get(f"https://ipapi.co/{i}/json/")
            data = res.json()
            city = data.get("city")
            country = data.get("country_name")
            region = data.get("region")
            if city and country:
                break
        return  f"{city},{region}, {country}"
    except:
        return "Unknown"
    
