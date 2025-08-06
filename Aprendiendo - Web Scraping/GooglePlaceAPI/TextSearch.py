import requests

api_key = "AIzaSyAXeXTV5CUqS9ExUK6pZV9Eg7GrSDLlSOs"  # Reemplaza con tu clave de API
location = "-33.868820,151.209290"  # Coordenadas de Sídney
radius = 10000  # Radio de búsqueda en metros (10 km)
place_type = "RESTAURANT"  # Tipo de lugar: restaurante (en mayúsculas)
keyword = "fast food" #palabra clave de busqueda
max_results = 10  # Número máximo de resultados

url = f"https://places.googleapis.com/v1/places:searchText" #cambio de endpoint

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating"
}

payload = {
    "textQuery": f"{keyword} {place_type}", #Combinamos palabra clave y tipo de lugar en textQuery
    "locationBias": { #cambiamos locationRestriction por locationBias
        "circle": {
            "center": {
                "latitude": float(location.split(",")[0]),
                "longitude": float(location.split(",")[1])
            },
            "radius": radius
        }
    },
    "maxResultCount": max_results
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    places = response.json().get("places", [])
    if places:
        sorted_places = sorted(places, key=lambda x: x.get("rating", 0), reverse=True)
        print("Los 10 mejores restaurantes de comida rápida en Sídney:")
        for place in sorted_places:
            name = place.get("displayName", {}).get("text", "Nombre no disponible")
            address = place.get("formattedAddress", "Dirección no disponible")
            rating = place.get("rating", "Puntuación no disponible")
            print(f"- {name} ({rating}): {address}")
    else:
        print("No se encontraron restaurantes de comida rápida.")
else:
    print(f"Error: {response.status_code} - {response.text}")