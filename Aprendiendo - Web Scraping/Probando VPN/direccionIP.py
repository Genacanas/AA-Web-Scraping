import requests

ip = requests.get('https://api64.ipify.org?format=json').json()["ip"]
print("Tu IP pública es:", ip)
