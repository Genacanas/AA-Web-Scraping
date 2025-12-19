import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json, re, logging
from fake_useragent import UserAgent
from urllib.parse import urljoin, unquote
import sys  # Used here to set console encoding on Windows

sys.stdout.reconfigure(encoding="utf-8")
ua = UserAgent()

# ===================================================================================================
# PARAMS
# ===================================================================================================
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

EMAIL_RE = re.compile(
    r"(?<![\/\w])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?!\.\w)"
)
BAD_SUBSTRINGS = ("tuemail", "ejemplo")
BAD_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")

CONTACT_PATTERNS = (
    "/contacto",
    "/contacto.html",
    "/contacto.htm",
    "/contacto.php",
    "/quienes-somos",
    "/nosotros",
    "/sobre-nosotros",
    "/acerca",
)

# status que **saltamos** (no renderizar)
SKIP_STATUS = {400, 404, 410, 422}


# ===================================================================================================
# HELPERS
# ===================================================================================================
def clean_email(e: str) -> str | None:
    if not e:
        return None
    e = e.strip().strip(").,;:>\"'")
    low = e.lower()
    if any(bad in low for bad in BAD_SUBSTRINGS):
        return None
    if any(low.endswith(ext) for ext in BAD_EXTENSIONS):
        return None
    return e


def extract_emails(soup: BeautifulSoup) -> set[str]:
    emails = set()
    # mailto:
    for a in soup.select('a[href^="mailto:"]'):
        href = a.get("href", "")
        email = unquote(href.split("mailto:", 1)[1].split("?", 1)[0])
        if e := clean_email(email):
            emails.add(e)
    # texto plano si aún no hay
    if not emails:
        for email in EMAIL_RE.findall(soup.get_text()):
            if e := clean_email(email):
                emails.add(e)
    return emails


def save_result(seed_info, emails, rendered, f_d, origin_url):
    f_d.append(
        {
            "id_resultado": seed_info.get("id_resultado"),
            "seed_id": seed_info.get("id"),
            "seed_title": seed_info.get("title"),
            "site_root": seed_info["url"],
            "source": rendered,  # home_HTML / home_JS / contact_HTML / contact_JS
            "source_url": origin_url,  # URL exacta de donde salió
            "emails": list(emails),
        }
    )
    logging.info(
        "Contacto (%s) encontrado en %s, emails: %d", rendered, origin_url, len(emails)
    )


# ===================================================================================================
# MAIN
# ===================================================================================================
if __name__ == "__main__":
    # cargar seeds únicas
    with open("urls.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    seen = set()
    seeds = []
    for item in data:
        site = (item.get("website") or "").strip()
        if site and site not in seen:
            seen.add(site)
            seeds.append(
                {"id": item.get("id"), "title": item.get("title"), "url": site}
            )

    logging.info("Semillas cargadas: %d sitios únicos", len(seeds))

    final_data = []
    i = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
        page = context.new_page()

        for seed in seeds:
            root = seed["url"]
            logging.info("Accediendo a %s", root)

            # ------------------ HTML plano Home ------------------
            try:
                r = requests.get(root, headers={"User-Agent": ua.chrome}, timeout=15)
                if r.status_code in SKIP_STATUS:
                    logging.warning("Página no válida (%s): %s", r.status_code, root)
                    continue
                if r.status_code != 200:
                    logging.warning("No se pudo acceder a %s: %s", root, r.status_code)
                    continue

                soup = BeautifulSoup(r.text, "html.parser")
                emails = extract_emails(soup)
                if emails:
                    seed["id_resultado"] = i
                    i += 1
                    save_result(seed, emails, "home_HTML", final_data, root)
                    continue
            except Exception as e:
                logging.error("Error accediendo a %s: %s", root, str(e))
                continue

            # ------------------ Render JS Home ------------------
            try:
                page.goto(root, wait_until="networkidle", timeout=4000)
                soup = BeautifulSoup(page.content(), "html.parser")
                emails = extract_emails(soup)
                if emails:
                    seed["id_resultado"] = i
                    i += 1
                    save_result(seed, emails, "home_JS", final_data, root)
                    continue

                logging.info("Sin contactos en home: %s", root)
            except Exception as e:
                logging.error("Error renderizando %s: %s", root, str(e))
                continue

            # ------------------ Búsqueda en endpoints de contacto ------------------
            contacto_encontrado = False

            for contact in CONTACT_PATTERNS:
                url = urljoin(root, contact)
                logging.info("Accediendo a %s", url)

                # -------- HTML plano Contacto
                try:
                    r = requests.get(url, headers={"User-Agent": ua.chrome}, timeout=15)
                    # si es 4xx de la lista => NO renderizamos y probamos el próximo sufijo
                    if r.status_code in SKIP_STATUS:
                        logging.warning("Página inválida (%s): %s", r.status_code, url)
                        continue
                    if r.status_code != 200:
                        logging.warning(
                            "No se pudo acceder a %s: %s", url, r.status_code
                        )
                        # 401/403/429, etc. (acá sí conviene intentar renderizar luego)
                    else:
                        soup = BeautifulSoup(r.text, "html.parser")
                        emails = extract_emails(soup)
                        if emails:
                            seed["id_resultado"] = i
                            i += 1
                            save_result(seed, emails, "contact_HTML", final_data, url)
                            contacto_encontrado = True
                            break
                        # endpoint correcto (200) pero sin emails -> no tiene sentido seguir probando otros sufijos
                        logging.info(
                            "Endpoint válido sin emails, deteniendo búsqueda de sufijos: %s",
                            url,
                        )
                        contacto_encontrado = True
                        break

                except Exception as e:
                    logging.error("Error accediendo a %s: %s", url, str(e))
                    # ante error de request seguimos al próximo sufijo
                    continue

                # -------- Render JS Contacto (solo si NO fue 4xx y aún no se marcó contacto_encontrado)
                if not contacto_encontrado:
                    logging.info("Renderizando con Playwright: %s", url)
                    try:
                        page.goto(url, wait_until="networkidle", timeout=4000)
                        soup = BeautifulSoup(page.content(), "html.parser")
                        emails = extract_emails(soup)
                        if emails:
                            seed["id_resultado"] = i
                            i += 1
                            save_result(seed, emails, "contact_JS", final_data, url)
                            contacto_encontrado = True
                            break

                        logging.info("No se encontraron contactos en: %s", url)
                    except Exception as e:
                        logging.error("Error renderizando %s: %s", url, str(e))
                        continue

            if not contacto_encontrado:
                logging.info("No se encontraron contactos para %s", root)

        browser.close()

    # ===================================================================================================
    # Guardado
    # ===================================================================================================
    with open("resultados_modif_11_11_25.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    logging.info(
        "Datos guardados en resultados_modif_11_11_25.json => Total sitios con contactos: %d",
        len(final_data),
    )
