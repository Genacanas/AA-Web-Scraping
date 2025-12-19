import requests
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
import json, re, logging
from fake_useragent import UserAgent
ua = UserAgent()
from urllib.parse import urljoin
from urllib.parse import unquote

# ===================================================================================================
# PARAMETROS GENERALES
# ===================================================================================================
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
EMAIL_RE = re.compile(
    r"(?<![\/\w])"  # que no esté justo después de / o palabra
    r"[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    r"(?!\.\w)"  # que no termine en algo raro tipo .js
)
BAD_SUBSTRINGS = ("tuemail", "ejemplo", "yourmail")
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

# ===================================================================================================
# Funcion para limpiar mails
# ===================================================================================================
def clean_email(e: str)-> str | None:
    if e is None:
        return None
    e = e.strip().strip(").,;:>\"'")
    low = e.lower()
    if any(bad in low for bad in BAD_SUBSTRINGS):
        return None
    if any(low.endswith(ext) for ext in BAD_EXTENSIONS):
        return None
    return e.strip()

# ===================================================================================================
# Funcion para extraer mails
# ===================================================================================================
def extract_emails(soup: BeautifulSoup) -> set[str]:
    emails = set()

    # Buscar en enlaces mailto:
    for a in soup.select('a[href^="mailto:"]'):
        href = a.get("href", "")
        email = unquote(href.split("mailto:", 1)[1].split("?", 1)[0])
        if e := clean_email(email):
            emails.add(e)

    # Si no hay emails, buscar en el texto
    if not emails:
        text = soup.get_text()
        found = EMAIL_RE.findall(text)
        for email in found:
            if e := clean_email(email):
                emails.add(e)

    return emails

# ===================================================================================================
# Funcion para guardar en final_data los resultados
# ===================================================================================================
def save_result(seed_info, emails, rendered, f_d):
    f_d.append({
        "id_resultado": seed_info.get("id_resultado"),
        "site_root": seed_info["url"],
        "seed_id": seed_info.get("id"),
        "seed_title": seed_info.get("title"),
        "emails": list(emails),
        "source": rendered,
    })
    logging.info("Contacto (%s) encontrado: %s, emails: %d", rendered, seed_info["url"], len(emails))

# ===================================================================================================
# Declaracion de variables gobales
# ===================================================================================================
json_file = "urls.json"
final_data = []
sufixes = ["html", "htm"]
i = 1
# ===================================================================================================
# MAIN
# ===================================================================================================
if __name__ == "__main__":
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)  # lista de objetos
    seen = set()
    seeds = []
    for item in data:
        site = (item.get("website") or "").strip()
        if site and site not in seen:
            seen.add(site)
            seeds.append(
                {
                 "id": item.get("id"), 
                 "title": item.get("title"), 
                 "url": site
                })


    logging.info("Semillas cargadas: %d sitios únicos", len(seeds))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, user_agent=ua.chrome)
        page = context.new_page()

        for seed in seeds:

            # -------- HTML plano Home
            try:
                logging.info("Accediendo a %s", seed["url"])
                response = requests.get(seed["url"], headers={"User-Agent": ua.chrome})
                if response.status_code != 200:
                    logging.warning("No se pudo acceder a %s: %s", seed["url"], response.status_code)
                    continue
                soup = BeautifulSoup(response.text, "html.parser")
                emails = extract_emails(soup)
                if emails:
                    seed["id_resultado"] = i
                    i += 1
                    save_result(seed_info=seed, emails=emails, rendered="home_HTML", f_d=final_data)
                    continue  # si ya encontró mails, no hace renderizado

                # Si no encontró mails, intentar con Playwright
                logging.info("Renderizando con Playwright: %s", seed["url"])

            except Exception as e:
                logging.error("Error accediendo a %s: %s", seed["url"], str(e))
                continue

            # -------- Render JS Home
            try:
                page.goto(seed["url"], wait_until="networkidle")
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                emails = extract_emails(soup)
                if emails:
                    seed["id_resultado"] = i
                    i += 1
                    save_result(seed_info=seed, emails=emails, rendered="home_JS", f_d=final_data)
                    continue  # si ya encontró mails, no sigue
                else:
                    logging.info("No se encontraron contactos en: %s", seed["url"])
            except Exception as e:
                logging.error("Error renderizando %s: %s", seed["url"], str(e))
                continue

            # Buscando en contacto
            for contact in CONTACT_PATTERNS:

                # -------- HTML plano Contacto

                url = urljoin(seed["url"], contact)
                logging.info("Accediendo a %s", url)

                try:
                    response = requests.get(url, headers={"User-Agent": ua.chrome})
                    if response.status_code != 200:
                        logging.warning("No se pudo acceder a %s: %s", url, response.status_code)
                        continue
                    soup = BeautifulSoup(response.text, "html.parser")
                    emails = extract_emails(soup)
                    if emails:
                        seed["id_resultado"] = i
                        i += 1
                        save_result(seed_info=seed, emails=emails, rendered="contact_HTML", f_d=final_data)
                        break  # si ya encontró mails, no sigue
                except Exception as e:
                    logging.error("Error accediendo a %s: %s", url, str(e))
                    continue

                # Si no encontró mails, intentar con Playwright
                logging.info("Renderizando con Playwright: %s", url)

                # -------- Render JS Contacto

                try:
                    page.goto(url, wait_until="networkidle")
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    emails = extract_emails(soup)
                    if emails:
                        seed["id_resultado"] = i
                        i += 1
                        save_result(seed_info=seed, emails=emails, rendered="contact_JS", f_d=final_data)
                        break  # si ya encontró mails, no sigue
                    else:
                        logging.info("No se encontraron contactos en: %s", url)
                except Exception as e:
                    logging.error("Error renderizando %s: %s", url, str(e))
                    continue

        browser.close()
    # ===================================================================================================
    # Guardado de datos en JSON  =>  resultados.json
    # ===================================================================================================
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    logging.info("Datos guardados en resultados.json  ==> Total sitios con contactos: %d", len(final_data))

    # ===================================================================================================
    # Guardado de datos en Excel  =>  Resultados.xlsx
    # ===================================================================================================
    # df = pd.DataFrame(final_data)
    # df.to_excel("Resultados.xlsx", index=False)
    # logging.info("Datos guardados en Resultados.xlsx  ==> Total sitios con contactos: %d", len(final_data))
