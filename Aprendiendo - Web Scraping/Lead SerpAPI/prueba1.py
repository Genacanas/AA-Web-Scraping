from serpapi import GoogleSearch
import pandas as pd
import json

for i in range(3,50):
    params = {
        "engine": "google",
        "q": "tiendas de venta de zapatillas multimarcas pequeñas en cordoba",
        "start": i,
        "api_key": "9f4b527edd7319403dbab8a75b8b162eedd15689a9d5ff01bac8fe88811401df"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Extrae solo los resultados orgánicos (pueden no existir si la búsqueda falla)
    organic_results = results.get("organic_results", [])

    # Guarda en JSON plano (si quieres el JSON completo):
    with open(f"results_full_{i}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    # Guarda solo los resultados orgánicos como DataFrame a JSON
    if organic_results:
        df = pd.DataFrame(organic_results)
        df.to_json(f"results_organic_{i}.json", orient="records", force_ascii=False, indent=4)
        print(f"Resultados guardados en 'results_organic_{i}.json'")
    else:
        print("No se encontraron resultados orgánicos.")
