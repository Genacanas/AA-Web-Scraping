from serpapi import GoogleSearch
import json

start_values = ["0", "20", "40", "60", "80"]

# Lista para acumular todos los resultados
all_results = []

for i in start_values:
    params = {
        "engine": "google_maps",
        "q": "soccer in Canada",
        "start": i,
        "type": "search",
        "api_key": "api_key_here",
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Agregar resultados si existen
    if "local_results" in results:
        all_results.extend(results["local_results"])

# Guardar todos los resultados en un archivo JSON
with open("zapaterias_cordoba.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print(f"Se guardaron {len(all_results)} resultados en zapaterias_cordoba.json")
