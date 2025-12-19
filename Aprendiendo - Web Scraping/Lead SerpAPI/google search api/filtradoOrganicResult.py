import json
import re
import pandas as pd
import os

data_final = []
folder = "Organic_results_JSON/" 
import os

print("Directorio actual:", os.getcwd())

for i in range(1, 48):
    filename = f"results_organic_{i}.json"
    filepath = f"C:/Users/feliu/OneDrive/Documentos/AA-Web-Scraping/Aprendiendo - Web Scraping/Lead SerpAPI/Organic results JSON/{filename}"

    try:
        print(f"Intentando abrir: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            for persona in data:
                if not re.search(r"tiktok", persona["link"], re.IGNORECASE):
                    data_final.append(
                        {
                            "file": f"results_organic_{i}.json",
                            "title": persona["title"],
                            "link": persona["link"],
                            "redirect_link": persona["redirect_link"],
                            "displayed_link": persona["displayed_link"],
                        }
                    )
    except FileNotFoundError:
        print(f"Archivo no encontrado: results_organic_{i}.json — se salta.")
    except Exception as e:
        print(f"Error al procesar results_organic_{i}.json: {e}")

# Guardar resultados
df = pd.DataFrame(data_final)
df.to_excel("results_organic.xlsx", index=False)
