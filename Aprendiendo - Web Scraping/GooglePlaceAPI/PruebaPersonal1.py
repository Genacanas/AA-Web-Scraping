import requests

#Definicion de Variables
API_KEY = "AIzaSyAXeXTV5CUqS9ExUK6pZV9Eg7GrSDLlSOs"
max_results = 10

#Construccion de la URL
url = f"https://places.googleapis.com/v1/places:searchText"

#Definicion de Headers
headers = {
    "Context-Type": "application/json", #Indico que estoy enviando un JSON
    "X-Goog-Api-Key": API_KEY, #Envio la API Key
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating" #Especificamos campos que obtendremos en la respuesta
}

#Construccion del payload de la solicitud
payload = {
    "textQuery": "Vet in New York City, United States",
    "maxResultCount": 10
} 

#Envio de la solicitud a la API
response = requests.post(url, headers=headers, json=payload)

#Procesamiento de la respuesta
if response.status_code == 200:
    places = response.json().get("places", [])
    print("10 Veterinarias en New York")
    i = 1
    for place in places:
        name = place.get("displayName", {}).get("text", "Nombre no disponible")
        address = place.get("formattedAddress", "Direccion no disponible")
        rating = place.get("rating", "Puntuacion no disponible")
        print(f"{i}. {name} ({rating}): {address}")
        i = i+1

else:
    print(f"Error: {response.status_code} - {response.text}")

