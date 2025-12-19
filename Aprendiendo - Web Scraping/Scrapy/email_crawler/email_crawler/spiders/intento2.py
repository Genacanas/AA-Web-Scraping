# spiders/contact_spider.py
import json, re
from urllib.parse import urljoin, urlparse
import scrapy
from scrapy_playwright.page import PageMethod

CONTACT_PATTERNS = (
    #"contact",
    "contacto",
    #"about",
    #"about-us",
    "nosotros",
    #"empresa",
    #"quienes",
    #"quiénes",
    #"impressum",
    #"legal",
    "ayuda",
    "soporte",
)

# EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EMAIL_RE = re.compile(
    r"(?<![\/\w])"  # que no esté justo después de / o palabra
    r"[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    r"(?!\.\w)"  # que no termine en algo raro tipo .js
)

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

class ContactSpider(scrapy.Spider):
    name = "contact_logic2"

    def __init__(self, json_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not json_file:
            raise ValueError("Pass -a json_file=urls.json")

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)  # lista de objetos

        seen = set()
        seeds = []
        for item in data:
            site = (item.get("website") or "").strip()
            if site and site not in seen:
                seen.add(site)
                seeds.append({
                    "url": site,
                    "id": item.get("id"),
                    "title": item.get("title")
                })

        #print(seeds) 
        #print(len(seeds))
        self.logger.info(f"Cargadas {len(seeds)} seeds de {json_file}")
        breakpoint()   
        self.seeds = seeds
        #hosts = {urlparse(s["url"]).netloc for s in self.seeds}
        #hosts |= {
        #    h.replace("www.", "") if h.startswith("www.") else f"www.{h}" for h in hosts
        #}
        #self.allowed_domains = list(hosts)
        #self.logger.info(f"allowed_domains: {self.allowed_domains}")
        #breakpoint()

    # ---------------- start ----------------
    def start_requests(self):
        # 1) Home SIN JS
        for s in self.seeds:
            yield scrapy.Request(
                s["url"],
                callback=self.parse_home_plain,
                meta={"seed": s, "stage": "home_plain"},  # tracking
            )

    # --------------- HOME ------------------
    def parse_home_plain(self, response):
        seed = response.meta["seed"]
        emails = self._extract_emails(response)
        self.logger.info(f"parse_home_plain: {response.url} - {emails}")
        if emails:
            for e in emails:
                yield self._item(seed, response.url, e, "home_plain")
            return
        # 2) Home CON JS (Playwright)
        yield scrapy.Request(
            seed["url"],
            callback=self.parse_home_js,
            meta={
                "seed": seed,
                "stage": "home_js",
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "networkidle"),
                    # Scroll hasta abajo para cargar contenido dinámico
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    #PageMethod("wait_for_timeout", 3000)
                ],
            },
            dont_filter=True,
        )

    def parse_home_js(self, response):
        seed = response.meta["seed"]
        emails = self._extract_emails(response)

        if "mulhaus" in response.url: 
            self.logger.info(response.text)
            breakpoint()

        self.logger.info(f"parse_home_js: {response.url} - {emails}")

        if emails:
            for e in emails:
                yield self._item(seed, response.url, e, "home_js")
            return
        # 3) Buscar enlaces de contacto SIN JS
        for url in self._contact_links(response):
            yield scrapy.Request(
                url,
                callback=self.parse_contact_plain,
                meta={"seed": seed, "stage": "contact_plain"},
            )

    # --------------- CONTACT ----------------
    def parse_contact_plain(self, response):
        seed = response.meta["seed"]

        # if "calzadosjimenez" in response.url and "contacto" in response.url:
        #    print("breakpoint contact_plain")
        #    breakpoint()

        emails = self._extract_emails(response)
        self.logger.info(f"parse_contact_plain: {response.url} - {emails}")
        if emails:
            for e in emails:
                yield self._item(seed, response.url, e, "contact_plain")
            return
        # 4) Misma página con JS
        yield scrapy.Request(
            response.url,
            callback=self.parse_contact_js,
            meta={
                "seed": seed,
                "stage": "contact_js",
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "networkidle"),
                    #PageMethod("wait_for_selector", 'a[href^="mailto:"]', timeout=7000),
                ],
            },
            dont_filter=True,
        )

    def parse_contact_js(self, response):
        seed = response.meta["seed"]
        emails = self._extract_emails(response)
        self.logger.info(f"parse_contact_js: {response.url} - {emails}")
        for e in emails:
            yield self._item(seed, response.url, e, "contact_js")

    # --------------- helpers ----------------
    #    def _extract_emails(self, response):
    #
    #        # mailtos = {
    #        #    h.replace("mailto:", "").strip()
    #        #    for h in response.css('a[href^="mailto:"]::attr(href)').getall()
    #        # }
    #
    #        all_hrefs = response.css('a[href^="mailto:"]::attr(href)').getall()
    #        for e in all_hrefs:
    #            potencial_email = e.replace("mailto:", "").strip()
    #            if EMAIL_RE.fullmatch(potencial_email):
    #                yield {"email": potencial_email, "url": response.url}
    #
    #        text = set(EMAIL_RE.findall(response.text or ""))
    #        #emails = mailtos | text
    #        #return sorted({e.strip(").,; ") for e in emails})
    # Supón que ya tienes EMAIL_RE = re.compile(r"...")  # tu regex de email

    def _extract_emails(self, response):
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

    # def _contact_links(self, response):
    #    urls = set()
    #    base = response.url
    #    for href in response.css("a::attr(href)").getall():
    #        if not href:
    #            continue
    #        if any(p in href.lower() for p in CONTACT_PATTERNS):
    #            url = urljoin(base, href)
    #            if urlparse(url).netloc == urlparse(base).netloc:
    #                urls.add(url)
    #    return urls

    # from urllib.parse import urljoin, urlparse

    def _contact_links(self, response):
        base = response.url
        same_host = urlparse(base).netloc
        found = set()

        # 1) Links reales presentes en el HTML
        for href in response.css("a::attr(href)").getall():
            if not href:
                continue
            if any(p in href.lower() for p in CONTACT_PATTERNS):
                url = urljoin(base, href)
                if urlparse(url).netloc == same_host and url not in found:
                    found.add(url)
                    yield url

        # 2) Fallbacks: si no encontramos nada, probamos rutas comunes
        if not found:
            # raíz del sitio
            root = f"{urlparse(base).scheme}://{same_host}/"
            guesses = set()

            # p, p/, p.html, p.htm y con prefijos de idioma típicos
            # prefixes = ("", "es/", "en/")
            for p in CONTACT_PATTERNS:
                # for pref in prefixes:
                guesses.update(
                    {
                        urljoin(root, f"{p}"),        #                       urljoin(root, f"{pref}{p}"),
                        urljoin(root, f"{p}/"),       #                       urljoin(root, f"{pref}{p}/"),
                        urljoin(root, f"{p}.html"),   #                       urljoin(root, f"{pref}{p}.html"),
                        urljoin(root, f"{p}.htm"),    #                       urljoin(root, f"{pref}{p}.htm"),
                    }
                )

            for url in guesses:
                # if "calzadosjimenez" in response.url and "contacto" in response.url:
                #    print ("breakpoint contact_links")
                #    breakpoint()
                # found.add(url)
                # mismo host y sin duplicados
                if urlparse(url).netloc == same_host and url not in found:
                    found.add(url)
                    yield url
        # return list(found)

    def _item(self, seed, page, email, source):

        return {
            "root": seed["url"],
            "page": page,
            "email": email,
            "source": source,  # home_plain, home_js, contact_plain, contact_js
            "seed_id": seed.get("id"),
            "seed_title": seed.get("title"),
        }


# ==============================================================================
# COMPILAR: scrapy crawl contact_logic2 -a json_file=urls.json -O salida3.json -s FEED_EXPORT_INDENT=4
# ==============================================================================
