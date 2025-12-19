import requests
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
import json, re, logging
from fake_useragent import UserAgent

ua = UserAgent()
from urllib.parse import urljoin
from urllib.parse import unquote
from urllib.parse import urlparse, urlunparse, parse_qs


# ===================================================================================================
# Funcion de extraccion del JSON de input
# ===================================================================================================

SOCIAL_FACEBOOK_DOMAINS = {
    "facebook.com",
    "es-la.facebook.com",
    "m.facebook.com",
    "web.facebook.com",
    "business.facebook.com",
    "touch.facebook.com",
    "l.facebook.com",
    "lm.facebook.com",
    "es-es.facebook.com",
    "b-m.facebook.com",
}
SOCIAL_INSTAGRAM_DOMAINS = {
    "instagram.com",
    "www.instagram.com",
    "m.instagram.com",
    "l.instagram.com",
}

BIO_LINK_DOMAINS = {  # por si querés tratarlos luego
    "linktr.ee",
    "beacons.ai",
    "bio.link",
    "taplink.cc",
    "carrd.co",
}


def _ensure_scheme(url: str) -> str:
    url = url.strip()
    if not re.match(r"^[a-z]+://", url, re.I):
        return "http://" + url
    return url


def _strip_tracking(u):
    """Quita fragmentos y, salvo redes, la query. Mantiene path base."""
    p = urlparse(u)
    cleaned = p._replace(params="", fragment="")
    # en redes suele haber query útil, pero normalmente no la necesitás para identificar perfil
    cleaned = cleaned._replace(query="")
    return urlunparse(cleaned)


def _unwrap_l_redirect(u: str) -> str:
    """
    Desenrolla enlaces tipo l.facebook.com/l.php?u=<destino>&...
    y l.instagram.com/...
    """
    p = urlparse(u)
    host = p.netloc.lower()
    if host in {"l.facebook.com", "lm.facebook.com"}:
        qs = parse_qs(p.query)
        cand = qs.get("u") or qs.get("href")  # facebook usa 'u' y a veces 'href'
        if cand and isinstance(cand, list) and cand[0]:
            return cand[0]
    if host == "l.instagram.com":
        qs = parse_qs(p.query)
        cand = qs.get("u")
        if cand and isinstance(cand, list) and cand[0]:
            return cand[0]
    return u


def normalize_url(raw: str) -> str | None:
    if not raw:
        return None
    try:
        u = _ensure_scheme(raw)
        u = _unwrap_l_redirect(u)
        p = urlparse(u)
        if not p.netloc:
            return None
        # normaliza www.
        host = p.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        cleaned = urlunparse((p.scheme, host, p.path, "", "", ""))
        return _strip_tracking(cleaned)
    except Exception:
        return None


def host_only(u: str) -> str:
    try:
        return urlparse(u).netloc.lower()
    except Exception:
        return ""


def classify_social(u: str) -> str | None:
    h = host_only(u)
    if h in SOCIAL_FACEBOOK_DOMAINS:
        return "facebook"
    if h in SOCIAL_INSTAGRAM_DOMAINS:
        return "instagram"
    if h in BIO_LINK_DOMAINS:
        return "bio_link"
    return None


def filtrar_sociales(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Devuelve (sociales, no_sociales)
    Cada elemento en 'sociales' trae:
      {id, title, website_original, website_normalized, social_type}
    """
    sociales, no_sociales = [], []
    vistos = set()  # evita duplicados por website_normalized
    for it in items:
        raw = (it.get("website") or "").strip()
        if not raw:
            no_sociales.append(it)
            continue

        norm = normalize_url(raw)
        if not norm:
            no_sociales.append(it)
            continue

        s_type = classify_social(norm)
        if s_type:
            key = (it.get("id"), norm)
            if key in vistos:
                continue
            vistos.add(key)
            sociales.append(
                {
                    "id": it.get("id"),
                    "title": it.get("title"),
                    "website_original": raw,
                    "website_normalized": norm,
                    "social_type": s_type,
                    "address": it.get("address")
                }
            )
        else:
            no_sociales.append(
                {**it, "website": norm}  # ya normalizada para tu prueba1.py
            )
    return sociales, no_sociales


# ===================================================================================================


with open("input.json", "r", encoding="utf-8") as f:
    data = json.load(f)

sociales, no_sociales = filtrar_sociales(data)

# Guarda para tus dos pipelines
with open("All_sociales.json", "w", encoding="utf-8") as f:
    json.dump(sociales, f, ensure_ascii=False, indent=4)

with open("All_no_sociales.json", "w", encoding="utf-8") as f:
    json.dump(no_sociales, f, ensure_ascii=False, indent=4)

print(f"Total items: {len(data)}")
print(f"Sociales: {len(sociales)}")
print(f"No sociales: {len(no_sociales)}")
