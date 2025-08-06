import re
import json
import requests
from bs4 import BeautifulSoup

# URL de la página a analizar
url = "https://filter-v9.globo.io/api/apiFilter?callback=jQuery37107188460932454195_1747862992989&filter_id=3955&shop=goecm.myshopify.com&collection=201902555285&sort_by=title-ascending&country=AR&limit=10000&event=init&cid=871d6e00-d950-4f07-8db4-ded1d9265c3d&did=ddcb40c4-75a0-4a40-9c1d-0caa14c0f24a&page_type=collection&ncp=1183"  # Reemplazá con la URL real

# Obtener HTML desde la URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"
}
response = requests.get(url, headers=headers)
html = response.text

# Parsear el HTML
soup = BeautifulSoup(html, "html.parser")

urls = []

# Buscar todos los <script> con contenido
for script in soup.find_all("script", id="web-pixels-manager-setup"):
    if not script.string:
        continue

    content = script.string

    # Buscar bloques que parezcan JSON dentro del script
    json_candidates = re.findall(r'({.*?})|(\[.*?\])', content, re.DOTALL)

    for group in json_candidates:
        for candidate in group:
            try:
                data = json.loads(candidate)
                # Serializar nuevamente para buscar URLs (por si están profundas)
                data_text = json.dumps(data)
                found_urls = re.findall(r'https?://[^\s"\'\\<>]+', data_text)
                urls.extend(found_urls)
            except json.JSONDecodeError:
                continue

# Eliminar duplicados
urls = list(set(urls))

# Mostrar resultado
for url in urls:
    print(url)
