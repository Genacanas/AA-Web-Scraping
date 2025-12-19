# -*- coding: utf-8 -*-
"""
Scraping Google Maps (SerpAPI) con paginación predicha por ciudad:
- CITY_SPECS ordenado XL -> L -> M -> S (sin Córdoba capital)
- coords_by_city = { "Ciudad": (lat, lon, 0, 20, ...) }
- Ejecuta 200 requests (para ir de 50 -> 250) agregando al mismo JSON
- Evita duplicados (place_id / data_id) y maneja errores
"""

from serpapi import GoogleSearch
import json, os, sys, time

# ---------------- Configuración ----------------
sys.stdout.reconfigure(encoding="utf-8")
API_KEY = "e8f4df3f8e920c694daa2da68d572d88e409fe0e34dea5cc0863d9b01d8c6166"

OUTFILE = "zapaterias_argentina.json"
REQUESTS_TO_MAKE = 200  # haces 200 nuevas (50 → 250)
SLEEP_BETWEEN = 0.20
HL = "es"
GL = "ar"
ZOOM = 15

# Paginación por TIER (predicción)
PAGES_BY_TIER = {
    "XL": [0, 20, 40, 60, 80],
    "L": [0, 20, 40, 60],
    "M": [0, 20, 40],
    "S": [0, 20],
}

# ---------------- CITY_SPECS (ordenado de XL a S) ----------------
# OJO: no incluimos Córdoba capital (a pedido). Conserva TODAS tus ciudades.
CITY_SPECS = {
    # === XL ===
    "Ciudad de Buenos Aires": (-34.6037, -58.3816, "XL"),
    "Rosario": (-32.9442, -60.6505, "XL"),
    "Mendoza": (-32.8895, -68.8458, "XL"),
    "San Miguel de Tucumán": (-26.8083, -65.2176, "XL"),
    "Salta": (-24.7821, -65.4232, "XL"),
    "Santa Fe": (-31.6336, -60.7000, "XL"),
    # === L ===
    "La Plata": (-34.9214, -57.9544, "L"),
    "Mar del Plata": (-38.0055, -57.5426, "L"),
    "Bahía Blanca": (-38.7196, -62.2724, "L"),
    "Neuquén": (-38.9516, -68.0591, "L"),
    "Posadas": (-27.3621, -55.9009, "L"),
    "Paraná": (-31.7319, -60.5238, "L"),
    "Resistencia": (-27.4516, -58.9867, "L"),
    "Corrientes": (-27.4692, -58.8306, "L"),
    "San Juan": (-31.5375, -68.5364, "L"),
    "San Luis": (-33.3017, -66.3378, "L"),
    "Santiago del Estero": (-27.7834, -64.2642, "L"),
    "San Salvador de Jujuy": (-24.1858, -65.2995, "L"),
    # === M ===
    "Quilmes": (-34.7242, -58.2526, "M"),
    "Lomas de Zamora": (-34.7609, -58.4067, "M"),
    "Lanús": (-34.7033, -58.3961, "M"),
    "Avellaneda": (-34.6620, -58.3644, "M"),
    "La Matanza (San Justo)": (-34.6766, -58.5600, "M"),
    "Tres de Febrero (Caseros)": (-34.6031, -58.5628, "M"),
    "San Isidro": (-34.4721, -58.5273, "M"),
    "Vicente López": (-34.5253, -58.4787, "M"),
    "Tigre": (-34.4260, -58.5796, "M"),
    "San Martín": (-34.5750, -58.5360, "M"),
    "Florencio Varela": (-34.8129, -58.2700, "M"),
    "Berazategui": (-34.7653, -58.2127, "M"),
    "Pilar": (-34.4570, -58.9136, "M"),
    "San Nicolás de los Arroyos": (-33.3350, -60.2252, "M"),
    "Tandil": (-37.3217, -59.1332, "M"),
    "Olavarría": (-36.8927, -60.3225, "M"),
    "Junín": (-34.5856, -60.9580, "M"),
    "Pergamino": (-33.8890, -60.5736, "M"),
    "Necochea": (-38.5545, -58.7396, "M"),
    "Campana": (-34.1687, -58.9593, "M"),
    "Zárate": (-34.0981, -59.0286, "M"),
    "Rio cuarto": (-33.1230, -64.3493, "M"),
    "Bariloche": (-41.1335, -71.3103, "M"),
    "Comodoro Rivadavia": (-45.8647, -67.4822, "M"),
    # === S ===
    "Ushuaia": (-54.8019, -68.3029, "S"),
    "Río Gallegos": (-51.6226, -69.2181, "S"),
    "San Rafael": (-34.6177, -68.3301, "S"),
    # También conservo las que ya habías procesado antes de Morón,
    # pero como dijiste que la corrida anterior terminó en Morón,
    # acá las dejamos igual en el mapping (no se ejecutan automáticamente más de 200 requests).
    #"Morón": (-34.6534, -58.6198, "M"),
}

# ---------------- Construcción de coords_by_city ----------------
coords_by_city = {
    city: tuple([lat, lon] + PAGES_BY_TIER[tier])
    for city, (lat, lon, tier) in CITY_SPECS.items()
}

# Chequeo informativo (requests planificadas por los tiers; el bucle corta en 200 igual)
planned_requests = sum(
    len(PAGES_BY_TIER[tier]) for _, (_, _, tier) in CITY_SPECS.items()
)
print(f"Requests planificadas por tiers (info): {planned_requests}")


# ---------------- Utilidades ----------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def serp_maps(city, lat, lon, start):
    params = {
        "engine": "google_maps",
        "q": f"zapaterias en {city}",
        "type": "search",
        "start": int(start),
        "hl": HL,
        "gl": GL,
        "ll": f"@{lat},{lon},{ZOOM}z",
        "api_key": API_KEY,
    }
    search = GoogleSearch(params)
    return search.get_dict()


# ---------------- Cargar acumulado y set de IDs únicos ----------------
all_results = load_json(OUTFILE, [])
seen_place_ids = set()
for r in all_results:
    pid = r.get("place_id") or r.get("data_id")
    if pid:
        seen_place_ids.add(pid)

# ---------------- Ejecutar 200 requests (agrega al JSON) ----------------
made = 0
for city, tup in coords_by_city.items():
    if made >= REQUESTS_TO_MAKE:
        break
    lat, lon, *starts = tup

    for start in starts:
        if made >= REQUESTS_TO_MAKE:
            break

        try:
            results = serp_maps(city, lat, lon, start)
        except Exception as e:
            print(f"[ERROR] {city} start={start} -> {e}")
            time.sleep(SLEEP_BETWEEN)
            continue

        if "error" in results:
            print(f"[ERROR] {city} start={start} -> {results['error']}")
            time.sleep(SLEEP_BETWEEN)
            continue

        made += 1
        local_results = results.get("local_results", [])
        if not local_results:
            print(f"[WARN] {city} start={start}: sin resultados (se continúa).")
        else:
            added = 0
            for r in local_results:
                pid = r.get("place_id") or r.get("data_id")
                if pid and pid in seen_place_ids:
                    continue
                if pid:
                    seen_place_ids.add(pid)
                r["__city_query"] = city
                r["__start"] = start
                all_results.append(r)
                added += 1
            print(f"[OK] {city} start={start} -> añadidos {added}")

        # Guardar en cada request
        save_json(OUTFILE, all_results)
        time.sleep(SLEEP_BETWEEN)

print("\n--- Resumen ---")
print(f"Requests nuevos (esta corrida): {made} / {REQUESTS_TO_MAKE}")
print(f"Resultados únicos acumulados: {len(all_results)}")
print(f"Guardado en {OUTFILE}")
