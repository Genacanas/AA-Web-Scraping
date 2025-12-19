import re
import json
from urllib.parse import urlparse

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request

try:
    from scrapy_playwright.page import PageCoroutine
except Exception:
    PageCoroutine = None

BAD_SUBSTRINGS = ("tuemail", "ejemplo")
BAD_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")


def clean_emails(candidates):
    valid = []
    for e in candidates:
        low = e.lower()
        if any(bad in low for bad in BAD_SUBSTRINGS):
            continue
        if any(low.endswith(ext) for ext in BAD_EXTENSIONS):
            continue
        valid.append(e)
    return valid


CONTACT_PATH_RE = (
    r"(?:\bcontact(?:o|us)?\b|quienes-?somos|nosotros|sobre-nosotros|about|acerca|empresa|home)"
)
EMAIL_RE = re.compile(
    r"(?<![\/\w])"  # que no esté justo después de / o palabra
    r"[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    r"(?!\.\w)"  # que no termine en algo raro tipo .js
)
# EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
# PHONE_RE = re.compile(r"\+?\d[\d\s().-]{6,}\d")


class ShoesContactSpider(CrawlSpider):
    name = "shoes_contacts_json"

    custom_settings = {
        "DEPTH_LIMIT": 6,
        "ROBOTSTXT_OBEY": True,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, json_file=None, *args, **kwargs):
        """
        Ejecuta con:
          scrapy crawl shoes_contacts_json -a json_file=urls.json
        """
        super().__init__(*args, **kwargs)
        if not json_file:
            raise ValueError("Debes pasar -a json_file=urls.json")

        # --- Leer archivo JSON y construir seeds ---
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        seen = set()
        seeds = []
        for item in data:
            site = (item.get("website") or "").strip()
            if site and site not in seen:
                seen.add(site)
                seeds.append(
                    {
                        "url": site,
                        "id": item.get("id"),
                        "title": item.get("title"),
                    }
                )

        if not seeds:
            raise ValueError("No se encontraron URLs válidas en el JSON.")

        self.start_urls = [s["url"] for s in seeds]
        self.allowed_domains = [urlparse(s["url"]).hostname for s in seeds]
        self._seeds = seeds  # guardamos los objetos completos
        self._done_domains = set()

        self.logger.info("Semillas cargadas: %d sitios únicos", len(seeds))

    # --- REGLAS ---
    rules = (
        Rule(
            LinkExtractor(allow=(CONTACT_PATH_RE,)),
            callback="parse_contact",
            follow=False,
        ),
        Rule(
            LinkExtractor(
                allow=(),
                deny=(
                    CONTACT_PATH_RE,
                    r"\.(?:pdf|jpe?g|png|gif|svg|webp|ico|css|js|zip|rar)(?:\?|$)",
                ),
            ),
            follow=True,
            process_request="process_request_general",
        ),
    )

    def process_request_general(self, request, response):
        netloc = urlparse(request.url).netloc
        if netloc in self._done_domains:
            return None
        return request

    # --- EXTRACCIÓN COMÚN ---
    def _extract_contacts(self, response):
        emails = set()          # es como una lista, pero evita duplicados

        # 1) Emails en enlaces <a href="mailto:...">
        for href in response.css('a[href^="mailto:"]::attr(href)').getall():
            # quita "mailto:" y cualquier parámetro tipo ?subject=...
            raw = href.replace("mailto:", "").split("?")[0].strip()
            if EMAIL_RE.fullmatch(raw):
                emails.add(raw)

        # 2) Emails en el texto de la página (no necesariamente enlazados)
        # Usar solo el texto visible reduce falsos positivos de scripts/estilos:
        """
        obtiene todo el texto visible dentro de <body>, como lista. 
        EJ: ["Bienvenido", "Contáctanos en", "info@empresa.com"] . 

        " ".join(...) junta esos fragmentos en un único string separados por espacios. 
        Resultado: "Bienvenido Contáctanos en info@empresa.com"

        Luego busca emails en ese string completo.
        """
        page_text = " ".join(response.css("body ::text").getall())
        for m in EMAIL_RE.findall(page_text or ""):
            emails.add(m)
        emails = clean_emails(emails)

        # if "calzadosjimenez" in response.url and "contacto" in response.url:
        #    print("breakpoint extract_emails")
        #    breakpoint()

        # Devuelve (o yield) todos, únicos y ordenados si quieres determinismo
        return sorted(emails)
        #emails = set(
        #    response.xpath('//a[starts-with(@href, "mailto:")]/@href').re(
        #        r"mailto:([^?]+)"
        #    )
        #)
        #emails |= set(EMAIL_RE.findall(response.text))
#
        ##phones = set(
        ##    response.xpath('//a[starts-with(@href, "tel:")]/@href').re(
        ##        r"tel:([\d+().\s-]+)"
        ##    )
        ##)
        ##phones |= set(PHONE_RE.findall(response.text))
        ##phones = {re.sub(r"[^\d+]", "", p) for p in phones}
#
        #emails = clean_emails(emails)
#
        #return sorted(emails)#, sorted(phones)

    # --- PARSEO DE CONTACTO (HTML ESTÁTICO) ---
    def parse_contact(self, response):
        netloc = urlparse(response.url).netloc
        seed_info = next(
            (s for s in self._seeds if urlparse(s["url"]).netloc == netloc), {}
        )
        emails = self._extract_contacts(response)

        item = {
            "site_root": f"{urlparse(response.url).scheme}://{netloc}",
            "url": response.url,
            "page_title": response.xpath("normalize-space(//title/text())").get(),
            "seed_id": seed_info.get("id"),
            "seed_title": seed_info.get("title"),
            "emails": emails,
            "rendered": False,
        }

        if emails:
            self._done_domains.add(netloc)
            self.logger.info("Contacto (HTML) encontrado: %s", netloc)
            yield item
            return

        # Si no hay datos, reintenta con Playwright (una sola vez)
        if not response.meta.get("rendered"):
            meta = dict(response.meta)
            meta["playwright"] = True
            meta["rendered"] = True
            if PageCoroutine:
                meta["playwright_page_coroutines"] = [
                    PageCoroutine("wait_for_load_state", "networkidle")
                ]

            yield Request(
                url=response.url,
                callback=self.parse_contact_js,
                meta=meta,
                dont_filter=True,
            )
        else:
            self.logger.info("Sin contactos en HTML ni JS: %s", response.url)
            yield item

    # --- PARSEO DE CONTACTO (JS RENDERIZADO) ---
    def parse_contact_js(self, response):
        netloc = urlparse(response.url).netloc
        seed_info = next(
            (s for s in self._seeds if urlparse(s["url"]).netloc == netloc), {}
        )
        emails = self._extract_contacts(response)

        item = {
            "site_root": f"{urlparse(response.url).scheme}://{netloc}",
            "url": response.url,
            "page_title": response.xpath("normalize-space(//title/text())").get(),
            "seed_id": seed_info.get("id"),
            "seed_title": seed_info.get("title"),
            "emails": emails,
            "rendered": True,
        }

        if emails:
            self._done_domains.add(netloc)
            self.logger.info("Contacto (JS) encontrado: %s", netloc)

        yield item
