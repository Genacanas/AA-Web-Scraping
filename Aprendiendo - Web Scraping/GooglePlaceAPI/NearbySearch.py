import requests

def buscar_lugares_cercanos(latitud, longitud, radio, tipo_lugar, clave_api, idioma="es"):
    """
    Realiza una búsqueda de lugares cercanos utilizando la API Places (nueva).

    Args:
        latitud (float): La latitud del centro del círculo de búsqueda.
        longitud (float): La longitud del centro del círculo de búsqueda.
        radio (int): El radio del círculo de búsqueda en metros.
        tipo_lugar (str): El tipo de lugar a buscar (por ejemplo, "restaurant", "cafe").
        clave_api (str): Tu clave de API de Google Maps Platform.
        idioma (str): El código de idioma para los resultados (opcional, por defecto "es").

    Returns:
        list: Una lista de diccionarios que representan los lugares encontrados, o None si hay un error.
    """

    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": clave_api,
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating"
    }

    payload = {
    "includedTypes": f"{tipo_lugar}", #Combinamos palabra clave y tipo de lugar en textQuery
    "locationRestriction": { #cambiamos locationRestriction por locationBias
        "circle": {
            "center": {
                "latitude": latitud,
                "longitude": longitud
            },
            "radius": radio
        }
    },
    "maxResultCount": 10
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
            print("No se encontraron restaurantes")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# Ejemplo de uso
clave_api = "AIzaSyAXeXTV5CUqS9ExUK6pZV9Eg7GrSDLlSOs"  # Reemplaza con tu clave de API real
latitud = 40.77481989326133   # Latitud de Nueva York
longitud = -74.07846065400302  # Longitud de Nueva York
radio = 1500  # Radio de búsqueda en metros
tipo_lugar = "restaurant"  # Tipo de lugar a buscar

lugares = buscar_lugares_cercanos(latitud, longitud, radio, tipo_lugar, clave_api)
