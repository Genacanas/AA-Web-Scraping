import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

import requests

url = "https://www.veterinaria24horas.ar/veterinaria/?url=veterinarias-en-rio-cuarto"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "es-ES,es;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "referer": "https://chatgpt.com/",
    "sec-ch-ua": '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
}

cookies = {
    "_gid": "GA1.2.556927489.1753648179",
    "_ga_305CM763P2": "GS2.1.s1753656092$o2$g0$t1753656092$j60$l0$h0",
    "_ga": "GA1.1.1334126337.1753648179",
    "_ga_HQ54KQR93T": "GS2.1.s1753656092$o2$g1$t1753656149$j3$l0$h0"
}

response = requests.get(url, headers=headers, cookies=cookies)

# # Verificás si se descargó correctamente
# print(response.status_code)
primerSplit = response.text.split("<!-- Cuerpo -->")[1]
data = primerSplit.split("<!-- Pie -->")[0]

soup = BeautifulSoup(data, "html.parser")
# print(soup)

# soup = BeautifulSoup(response.text, "html.parser")

datos = []

# buscar los <h3> que contienen nombres
titulos = soup.select("div.cuerpo-nota h3")

for titulo in titulos:
    nombre = titulo.get_text(strip=True)
    siguiente = titulo.find_next_sibling()

    direccion = ""
    telefono = ""

    while siguiente and siguiente.name != "h3":
        texto = siguiente.get_text(strip=True)

        # Buscar dirección si contiene la palabra 'Dirección'
        if "Dirección" in texto:
            # Normalmente el texto de la dirección está después del span "Dirección:"
            direccion_match = re.search(r"Dirección:\s*(.+)", texto)
            if direccion_match:
                direccion = direccion_match.group(1).strip()
            else:
                # Alternativa: si está en el siguiente elemento
                siguiente2 = siguiente.find_next_sibling()
                if siguiente2:
                    direccion = siguiente2.get_text(strip=True)

        # Buscar número de teléfono con regex (ej: 0351-xxxxxxx)
        telefono_match = re.search(r"\b0?358.*", texto)
        if telefono_match:
            telefono = telefono_match.group(0)

        siguiente = siguiente.find_next_sibling()

    datos.append({
        "nombre": nombre,
        "direccion": direccion,
        "telefono": telefono
    })

# Mostrar resultados
for d in datos:
    print(d)

# Guardar en Excel (opcional)
df = pd.DataFrame(datos)
df.to_excel("veterinarias_rioCuarto_v2.xlsx", index=False)
