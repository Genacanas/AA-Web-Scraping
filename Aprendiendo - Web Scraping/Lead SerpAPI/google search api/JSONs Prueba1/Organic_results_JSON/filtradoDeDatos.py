import json
import glob
import os

# Carpetas y patrones
file_pattern = "results_organic_*.json"

# Dominios que queremos excluir (agregá más si querés)
excluir = [
    "tiktok.com", "facebook.com", "instagram.com", "twitter.com", "youtube.com",
    "pinterest.com"
]

# Función para saber si el link es de un sitio útil
def es_util(link):
    return not any(dominio in link for dominio in excluir)

# Lista para almacenar resultados filtrados
resultados_utiles = []

# Recorremos todos los archivos que coinciden con el patrón
folder = r"C:\Users\genar\OneDrive\Documentos\AA Web Scraping\Aprendiendo - Web Scraping\Lead SerpAPI\JSONs Prueba1\Organic Results JSON"

for i in range(1, 47):
    file_path = os.path.join(folder, f"results_organic_{i}.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # ... resto del código ...


        for item in data:
            link = item.get("link", "")
            title = item.get("title", "")
            if es_util(link):
                resultados_utiles.append({"title": title, "link": link})

# Mostramos los resultados o los guardamos en archivo
for r in resultados_utiles:
    print(f"{r['title']} -> {r['link']}")

# Guardar en un nuevo archivo JSON (opcional)
with open("resultados_filtrados.json", "w", encoding="utf-8") as f:
    json.dump(resultados_utiles, f, ensure_ascii=False, indent=4)
