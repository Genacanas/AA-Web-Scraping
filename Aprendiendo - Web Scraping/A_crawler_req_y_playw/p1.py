import requests

url = "https://zillow-com1.p.rapidapi.com/agentDetails"

querystring = {"username": "kkladakis1"}

headers = {"x-rapidapi-host": "zillow-com1.p.rapidapi.com"}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
