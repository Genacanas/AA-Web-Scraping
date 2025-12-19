from urllib.parse import urlparse, parse_qs
import json


def filtrar_sociales_simple(items):
    sociales, no_sociales = [], []
    index_social = 1
    index_no_social = 1

    for it in items:
        raw = (it.get("website") or "").strip()
        if not raw:
            it["index"] = index_no_social
            index_no_social += 1
            no_sociales.append(it)
            continue

        url = raw
        low = url.lower()

        if "l.facebook.com" in low or "l.instagram.com" in low:
            try:
                p = urlparse(url)
                qs = parse_qs(p.query)
                if "u" in qs and qs["u"]:
                    url = qs["u"][0]
                    low = url.lower()
            except Exception:
                pass

        if "facebook" in low:
            sociales.append(
                {
                    "index": index_social,
                    "title": it.get("title"),
                    "website_original": raw,
                    "website_normalized": url,
                    "social_type": "facebook",
                    "phone": it.get("phone"),
                    "address": it.get("address"),
                }
            )
            index_social += 1
        elif "instagram" in low:
            sociales.append(
                {
                    "index": index_social,
                    "title": it.get("title"),
                    "website_original": raw,
                    "website_normalized": url,
                    "social_type": "instagram",
                    "phone": it.get("phone"),
                    "address": it.get("address"),
                }
            )
            index_social += 1
        else:
            no_sociales.append({
                "index": index_no_social,
                "title": it.get("title"),
                "website": it.get("website"),
                "phone": it.get("phone"),
                "address": it.get("address"),
            })
            index_no_social += 1

    return sociales, no_sociales


with open("data/input.json", "r", encoding="utf-8") as f:
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

with open("data/sociales.json", "w", encoding="utf-8") as f:
    json.dump(sociales, f, ensure_ascii=False, indent=2)

with open("data/no_sociales.json", "w", encoding="utf-8") as f:
    json.dump(no_sociales, f, ensure_ascii=False, indent=2)

with open("data/rest.json", "w", encoding="utf-8") as f:
    json.dump(rest, f, ensure_ascii=False, indent=2)

print(f"Total items: {len(data)}")
print(f"Sociales: {len(sociales)}")
print(f"No sociales: {len(no_sociales)}")
print(f"Restantes: {len(rest)}")
