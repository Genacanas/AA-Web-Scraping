from serpapi import GoogleSearch
import json, time
import sys

sys.stdout.reconfigure(encoding="utf-8")

API_KEY = "e8f4df3f8e920c694daa2da68d572d88e409fe0e34dea5cc0863d9b01d8c6166"

start_values = [0, 20, 40, 60, 80]
ubication_values = [
    # Prioridad máxima
    "Ciudad de Buenos Aires",

    # Provincia de Buenos Aires (muy prioritarias primero)
    "La Plata", "Mar del Plata", "Bahía Blanca", "Quilmes", "Lomas de Zamora",
    "Lanús", "Avellaneda", "La Matanza (San Justo)", "Morón", "Tres de Febrero (Caseros)",
    "San Isidro", "Vicente López", "Tigre", "San Martín", "Florencio Varela",
    "Berazategui", "Pilar", "San Nicolás de los Arroyos", "Tandil", "Olavarría",
    "Junín", "Pergamino", "Necochea", "Campana", "Zárate",

    # Resto de provincias (en orden de importancia general)
    "Rosario", "Mendoza", "San Miguel de Tucumán", "Salta", "Santa Fe","Rio cuarto",
    "Neuquén", "Posadas", "Paraná", "Resistencia", "Corrientes",
    "San Juan", "San Luis", "Santiago del Estero", "San Salvador de Jujuy",
    "Bariloche", "Comodoro Rivadavia", "Ushuaia", "Río Gallegos",
    "San Rafael"
]
# 46 aquí porque quitaste varias; si querés 50, agrega 4 más.

coords_by_city = {
    "Ciudad de Buenos Aires": (-34.6037, -58.3816),
    "La Plata": (-34.9214, -57.9544),
    "Mar del Plata": (-38.0055, -57.5426),
    "Bahía Blanca": (-38.7196, -62.2724),
    "Quilmes": (-34.7242, -58.2526),
    "Lomas de Zamora": (-34.7609, -58.4067),
    "Lanús": (-34.7033, -58.3961),
    "Avellaneda": (-34.6620, -58.3644),
    "La Matanza (San Justo)": (-34.6766, -58.5600),
    "Morón": (-34.6534, -58.6198),
    "Tres de Febrero (Caseros)": (-34.6031, -58.5628),
    "San Isidro": (-34.4721, -58.5273),
    "Vicente López": (-34.5253, -58.4787),
    "Tigre": (-34.4260, -58.5796),
    "San Martín": (-34.5750, -58.5360),
    "Florencio Varela": (-34.8129, -58.2700),
    "Berazategui": (-34.7653, -58.2127),
    "Pilar": (-34.4570, -58.9136),
    "San Nicolás de los Arroyos": (-33.3350, -60.2252),
    "Tandil": (-37.3217, -59.1332),
    "Olavarría": (-36.8927, -60.3225),
    "Junín": (-34.5856, -60.9580),
    "Pergamino": (-33.8890, -60.5736),
    "Necochea": (-38.5545, -58.7396),
    "Campana": (-34.1687, -58.9593),
    "Zárate": (-34.0981, -59.0286),
    "Rosario": (-32.9442, -60.6505),
    "Mendoza": (-32.8895, -68.8458),
    "San Miguel de Tucumán": (-26.8083, -65.2176),
    "Salta": (-24.7821, -65.4232),
    "Santa Fe": (-31.6336, -60.7000),
    "Rio cuarto": (-33.1230, -64.3493),
    "Neuquén": (-38.9516, -68.0591),
    "Posadas": (-27.3621, -55.9009),
    "Paraná": (-31.7319, -60.5238),
    "Resistencia": (-27.4516, -58.9867),
    "Corrientes": (-27.4692, -58.8306),
    "San Juan": (-31.5375, -68.5364),
    "San Luis": (-33.3017, -66.3378),
    "Santiago del Estero": (-27.7834, -64.2642),
    "San Salvador de Jujuy": (-24.1858, -65.2995),
    "Bariloche": (-41.1335, -71.3103),
    "Comodoro Rivadavia": (-45.8647, -67.4822),
    "Ushuaia": (-54.8019, -68.3029),
    "Río Gallegos": (-51.6226, -69.2181),
    "San Rafael": (-34.6177, -68.3301),
}


all_results = []
seen_place_ids = set()

max_requests = 50
made = 0

for city in ubication_values:
    for start in start_values:
        if made >= max_requests:
            break

        lat, lon = coords_by_city[city]
        params = {
            "engine": "google_maps",
            "q": f"zapaterias en {city}",
            "type": "search",
            "start": start,
            "hl": "es",
            "gl": "ar",
            "ll": f"@{lat},{lon},15z",  # centra la búsqueda en la ciudad
            "api_key": API_KEY,
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        made += 1
        if "local_results" not in results:
            print(f"[WARN] No local_results for {city} start={start}")
            continue

        # agrega resultados si existen
        for r in results.get("local_results", []):
            pid = r.get("place_id") or r.get("data_id")
            if pid and pid in seen_place_ids:
                continue
            if pid:
                seen_place_ids.add(pid)
            r["__city_query"] = city    # guarda de qué ciudad vino
            r["__start"] = start
            all_results.append(r)

        print(f"[OK] {city} start={start} → req {made}/{max_requests}")

        # opcional: pequeña pausa para ser amable con el rate limit
        time.sleep(0.2)

# guardar
outfile = "zapaterias_argentina.json"
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"Requests hechos: {made}")
print(f"Resultados únicos: {len(all_results)}")
print(f"Guardado en {outfile}")
