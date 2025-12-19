import json
import logging


filtred_data = []
with open("zapaterias_cordoba.json", 'r', encoding='utf-8') as f:
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
        

with open("zapaterias_cordoba_filtred.json", 'w', encoding='utf-8') as f:
    json.dump(filtred_data, f, ensure_ascii=False, indent=4)

print(f"Se guardaron {len(filtred_data)} resultados filtrados en zapaterias_cordoba_filtred.json")
