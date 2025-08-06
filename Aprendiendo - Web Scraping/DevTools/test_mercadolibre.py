import requests

url = "https://openweathermap.org/themes/openweathermap/assets/vendor/mosaic/data/wind-direction-short-data.json"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
data = response.json()

print(data)
