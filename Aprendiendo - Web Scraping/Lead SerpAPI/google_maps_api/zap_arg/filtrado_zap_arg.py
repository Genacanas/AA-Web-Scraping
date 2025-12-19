import json
import logging
import sys

# ---------------- Configuración ----------------
sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(message)s")

filtred_data = []
with open("zapaterias_argentina.json", "r", encoding="utf-8") as f:
    data = json.load(f)

    for j, item in enumerate(data, start=1):
        filtred_item = {
            "id": j,
            "title": item.get("title"),
            "phone": item.get("phone"),
            "website": item.get("website"),
            "address": item.get("address"),
        }
        filtred_data.append(filtred_item)
        logging.info(f"Procesado {j}: {filtred_item['title']}")

with open("zapaterias_argentina_filtred.json", "w", encoding="utf-8") as f:
    json.dump(filtred_data, f, ensure_ascii=False, indent=4)

print(
    f"Se guardaron {len(filtred_data)} resultados filtrados en zapaterias_argentina_filtred.json"
)
