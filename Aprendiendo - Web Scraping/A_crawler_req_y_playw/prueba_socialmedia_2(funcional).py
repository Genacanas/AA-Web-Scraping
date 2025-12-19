from urllib.parse import urlparse, parse_qs
import json

def filtrar_sociales_simple(items):
    """
    items: lista de dicts con al menos: { "id", "title", "website" }
    Devuelve (sociales, no_sociales).

    Regla: si 'facebook' o 'instagram' aparece en la URL (case-insensitive),
    lo clasifico como red social. Todo lo demás va a no_sociales.
    """
    sociales, no_sociales = [], []

    for it in items:
        raw = (it.get("website") or "").strip()
        if not raw:
            no_sociales.append(it)
            continue

        url = raw  # por si la querés conservar
        low = url.lower()

        # Desenrollado mínimo de l.facebook.com / l.instagram.com (común en GMaps)
        if "l.facebook.com" in low or "l.instagram.com" in low:
            try:
                p = urlparse(url)
                qs = parse_qs(p.query)
                if "u" in qs and qs["u"]:
                    url = qs["u"][0]
                    low = url.lower()
            except Exception:
                pass  # si falla, seguimos con la original

        # Clasificación súper simple
        if "facebook" in low:
            sociales.append(
                {
                    "id": it.get("id"),
                    "title": it.get("title"),
                    "website_original": raw,
                    "website_normalized": url,
                    "social_type": "facebook",
                    "phone": it.get("phone"),
                    "address": it.get("address"),
                }
            )
        elif "instagram" in low:
            sociales.append(
                {
                    "id": it.get("id"),
                    "title": it.get("title"),
                    "website_original": raw,
                    "website_normalized": url,
                    "social_type": "instagram",
                    "phone": it.get("phone"),
                    "address": it.get("address"),
                }
            )
        else:
            # lo que no matchea redes, va para tu pipeline de webs (prueba1.py)
            out = dict(it)
            out["website"] = url  # por si quedó desenrollada
            no_sociales.append(out)

    return sociales, no_sociales


with open("input.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    seen = set()
    seeds = []
    rest = []
    for item in data:
        site = (item.get("website") or "").strip()
        if site and site not in seen:
            seen.add(site)
            seeds.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "website": site,
                    "phone": item.get("phone"),
                    "address": item.get("address"),
                }
            )
        else:
            # lo que no matchea redes, va para tu pipeline de webs (prueba1.py)
            out = dict(item)
            out["website"] = site  # por si quedó desenrollada
            rest.append(out)

sociales, no_sociales = filtrar_sociales_simple(seeds)

with open("All_sociales_2.json", "w", encoding="utf-8") as f:
    json.dump(sociales, f, ensure_ascii=False, indent=2)

with open("All_no_sociales_2.json", "w", encoding="utf-8") as f:
    json.dump(no_sociales, f, ensure_ascii=False, indent=2)

with open("All_rest_2.json", "w", encoding="utf-8") as f:
    json.dump(rest, f, ensure_ascii=False, indent=2)

print(f"Total items: {len(data)}")
print(f"Sociales: {len(sociales)}")
print(f"No sociales: {len(no_sociales)}")
print(f"Restantes: {len(rest)}")