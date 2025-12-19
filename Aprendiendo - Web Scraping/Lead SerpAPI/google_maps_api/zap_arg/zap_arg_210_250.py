# -*- coding: utf-8 -*-
from serpapi import GoogleSearch
import json, os, sys, time, re

sys.stdout.reconfigure(encoding="utf-8")

API_KEY = "e8f4df3f8e920c694daa2da68d572d88e409fe0e34dea5cc0863d9b01d8c6166"
OUTFILE = "zapaterias_argentina.json"
LOGFILE = "zap_arg_50_209.log"  # el que adjuntaste
HL, GL, ZOOM = "es", "ar", 15

REQUESTS_TO_MAKE = 41
SLEEP = 0.2


# ---------- Helpers ----------
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
    return GoogleSearch(params).get_dict()


# ---------- 1) Parsear el .log para decidir reintentos ----------
# Ejemplos del log:
# [OK] Rosario start=80 -> añadidos 17
# [ERROR] Posadas start=60 -> Google hasn't returned any results for this query.
pattern_ok = re.compile(r"^\[OK\]\s+(.*?)\s+start=(\d+)\s+-> añadidos\s+(\d+)$")
pattern_err = re.compile(r"^\[ERROR\]\s+(.*?)\s+start=(\d+)\s+->")

city_entries = {}
with open(LOGFILE, "r", encoding="utf-8") as f:
    for line in (l.strip() for l in f):
        m = pattern_ok.match(line)
        if m:
            city = m.group(1)
            start = int(m.group(2))
            added = int(m.group(3))
            city_entries.setdefault(city, []).append(("ok", start, added))
            continue
        m = pattern_err.match(line)
        if m:
            city = m.group(1)
            start = int(m.group(2))
            city_entries.setdefault(city, []).append(("err", start, None))


# Determinar, para cada ciudad, el "último ok" y si hay un next_start viable
def next_start_if_promising(entries):
    """
    entries: list of tuples ("ok"/"err", start, added)
    return (next_start) or None
    Regla:
      - tomar el último OK (mayor start con "ok")
      - si added >= 10 y next_start <= 80 y NO hay un error registrado en next_start => devolver next_start
    """
    if not entries:
        return None
    entries_sorted = sorted(entries, key=lambda x: x[1])
    last_ok = None
    seen_err = {st for typ, st, _ in entries_sorted if typ == "err"}
    for typ, st, added in entries_sorted:
        if typ == "ok":
            last_ok = (st, added)
    if not last_ok:
        return None
    st, added = last_ok
    if added < 10 or st >= 80:
        return None
    candidate = st + 20
    if candidate in seen_err:
        return None
    return candidate


# Coordenadas de TODAS las ciudades que aparecen en el log (las de tu lista anterior)
coords_known = {
    "Ciudad de Buenos Aires": (-34.6037, -58.3816),
    "Rosario": (-32.9442, -60.6505),
    "Mendoza": (-32.8895, -68.8458),
    "San Miguel de Tucumán": (-26.8083, -65.2176),
    "Salta": (-24.7821, -65.4232),
    "Santa Fe": (-31.6336, -60.7000),
    "La Plata": (-34.9214, -57.9544),
    "Mar del Plata": (-38.0055, -57.5426),
    "Bahía Blanca": (-38.7196, -62.2724),
    "Neuquén": (-38.9516, -68.0591),
    "Posadas": (-27.3621, -55.9009),
    "Paraná": (-31.7319, -60.5238),
    "Resistencia": (-27.4516, -58.9867),
    "Corrientes": (-27.4692, -58.8306),
    "San Juan": (-31.5375, -68.5364),
    "San Luis": (-33.3017, -66.3378),
    "Santiago del Estero": (-27.7834, -64.2642),
    "San Salvador de Jujuy": (-24.1858, -65.2995),
    "Quilmes": (-34.7242, -58.2526),
    "Lomas de Zamora": (-34.7609, -58.4067),
    "Lanús": (-34.7033, -58.3961),
    "Avellaneda": (-34.6620, -58.3644),
    "La Matanza (San Justo)": (-34.6766, -58.5600),
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
    "Rio cuarto": (-33.1230, -64.3493),
    "Bariloche": (-41.1335, -71.3103),
    "Comodoro Rivadavia": (-45.8647, -67.4822),
    "Ushuaia": (-54.8019, -68.3029),
    "Río Gallegos": (-51.6226, -69.2181),
    "San Rafael": (-34.6177, -68.3301),
}

# Construir lista de reintentos a partir del log
retries = []
for city, entries in city_entries.items():
    nxt = next_start_if_promising(entries)
    if nxt is not None and city in coords_known:
        retries.append((city, coords_known[city][0], coords_known[city][1], nxt))

# Ordenar solo para que el output sea predecible
retries.sort(key=lambda x: (x[0], x[3]))

print("Reintentos detectados en log:", len(retries))
for c, la, lo, st in retries:
    print(f" - {c} next_start={st}")

# ---------- 2) Pool de ciudades nuevas (S=[0,20], M=[0,20,40]) ----------
PAGES_BY_TIER = {"M": [0, 20, 40], "S": [0, 20]}

NEW_CITY_SPECS = {
    # AMBA / PBA interior (no usadas en tu corrida anterior actual)
    "Ituzaingó": (-34.6570, -58.6773, "S"),
    "Hurlingham": (-34.5899, -58.6394, "S"),
    "José C. Paz": (-34.5150, -58.7745, "S"),
    "Malvinas Argentinas": (-34.4969, -58.7092, "S"),
    "Escobar": (-34.3499, -58.7934, "S"),
    "Luján (BA)": (-34.5703, -59.1050, "S"),
    "San Pedro (BA)": (-33.6833, -59.6667, "S"),
    "Mercedes (BA)": (-34.6515, -59.4307, "S"),
    "Chivilcoy": (-34.8960, -60.0167, "S"),
    "Azul": (-36.7790, -59.8616, "S"),
    "Bragado": (-35.1180, -60.4870, "S"),
    "Saladillo": (-35.6372, -59.7770, "S"),
    "Chascomús": (-35.5743, -58.0096, "S"),
    "General Rodríguez": (-34.6096, -58.9487, "S"),
    "Cañuelas": (-35.0544, -58.7558, "S"),
    "Lobos": (-35.1840, -59.0940, "S"),
    # Litoral / NEA / NOA internos
    "Gualeguaychú": (-33.0103, -58.5126, "S"),
    "Gualeguay": (-33.1423, -59.3180, "S"),
    "Victoria": (-32.6196, -60.1547, "S"),
    "Rafaela": (-31.2503, -61.4867, "M"),
    "Reconquista": (-29.1455, -59.6417, "S"),
    "Venado Tuerto": (-33.7456, -61.9688, "M"),
    # Patagonia norte/sur
    "Viedma": (-40.8135, -63.0000, "S"),
    "General Roca": (-39.0333, -67.5833, "M"),
    "Cipolletti": (-38.9333, -68.0000, "S"),
    "Plottier": (-38.9667, -68.2333, "S"),
    "Cutral Co": (-38.9387, -69.2332, "S"),
    "Zapala": (-38.8992, -70.0544, "S"),
    "Caleta Olivia": (-46.4390, -67.5280, "S"),
    "Río Grande": (-53.7877, -67.7096, "S"),
    "Tolhuin": (-54.5085, -67.1951, "S"),
}


# Expandir a (lat,lon, starts…)
def expand(specs):
    out = {}
    for city, (lat, lon, tier) in specs.items():
        out[city] = (lat, lon, *PAGES_BY_TIER[tier])
    return out


new_coords = expand(NEW_CITY_SPECS)

# ---------- 3) Ejecutar exactamente 41 requests ----------
# Cargar JSON acumulado para evitar duplicados
all_results = load_json(OUTFILE, [])
seen_place_ids = set()
for r in all_results:
    pid = r.get("place_id") or r.get("data_id")
    if pid:
        seen_place_ids.add(pid)

# Armar lista final de tareas: (city, lat, lon, start)
tasks = []

# Primero, los reintentos (13 detectados)
tasks.extend(retries)

# Luego, rellenar con nuevas ciudades hasta llegar a 41
if len(tasks) < REQUESTS_TO_MAKE:
    remaining = REQUESTS_TO_MAKE - len(tasks)
    for city, tpl in new_coords.items():
        lat, lon, *starts = tpl
        for st in starts:
            tasks.append((city, lat, lon, st))
            if len(tasks) >= REQUESTS_TO_MAKE:
                break
        if len(tasks) >= REQUESTS_TO_MAKE:
            break

print(f"\nTotal de tareas armadas: {len(tasks)} (objetivo {REQUESTS_TO_MAKE})")
# Ejecutar
made = 0
for city, lat, lon, start in tasks:
    try:
        results = serp_maps(city, lat, lon, start)
    except Exception as e:
        print(f"[ERROR] {city} start={start} -> {e}")
        time.sleep(SLEEP)
        continue
    if "error" in results:
        print(f"[ERROR] {city} start={start} -> {results['error']}")
        time.sleep(SLEEP)
        continue

    made += 1
    local_results = results.get("local_results", [])
    if not local_results:
        print(f"[WARN] {city} start={start}: sin resultados.")
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

    # Guardar en cada vuelta
    save_json(OUTFILE, all_results)
    time.sleep(SLEEP)

print("\n--- Resumen 41 ---")
print(f"Requests ejecutadas: {made}/{REQUESTS_TO_MAKE}")
print(f"Resultados únicos acumulados: {len(all_results)}")
print(f"Guardado en {OUTFILE}")
