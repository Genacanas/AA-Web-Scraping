# spiders/contact_spider.py
import scrapy, re, json
from urllib.parse import urljoin, urlparse
from urllib.parse import urlparse

CONTACT_PATTERNS = (
    "contact",
    "contacto",
    "about",
    "nosotros",
    "empresa",
    "quienes",
    "quiénes",
    "impressum",
)

# EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)+")
# EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EMAIL_RE = re.compile(
    r"(?<![\/\w])"  # que no esté justo después de / o palabra
    r"[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    r"(?!\.\w)"  # que no termine en algo raro tipo .js
)


class ContactSpider(scrapy.Spider):
    name = "contact_logic"


    def __init__(self, json_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not json_file:
            raise ValueError("Pass -a json_file=urls.json")

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)  # ahora es una lista de dicts

        # Tomar solo los primeros 5 items que tengan website no vacío
        urls = []
        for item in data[:15]:
            if item.get("website"):
                urls.append(item["website"])

        self.start_urls = urls
        self.allowed_domains = list({urlparse(u).netloc for u in self.start_urls})


    def parse(self, response):
        # 1) Buscar emails en la página principal
        emails = self._extract_emails(response)
        if emails:
            for e in emails:
                yield {
                    "root": response.url,
                    "page": response.url,
                    "email": e,
                    "source": "home",
                }
            return  # ← si encontró en home, NO sigue a /contacto

        # 2) No hubo emails en home → buscar links de contacto y visitarlos
        for href in response.css("a::attr(href)").getall():
            if not href:
                continue
            if any(p in href.lower() for p in CONTACT_PATTERNS):
                url = urljoin(response.url, href)
                # solo mismo dominio
                if urlparse(url).netloc == urlparse(response.url).netloc:
                    yield scrapy.Request(
                        url, callback=self.parse_contact, meta={"root": response.url}
                    )

    def parse_contact(self, response):
        # Extraer emails en la página de contacto/about
        emails = self._extract_emails(response)
        for e in emails:
            yield {
                "root": response.meta.get("root", response.url),
                "page": response.url,
                "email": e,
                "source": "contact",
            }

    # -------- helpers --------
    def _extract_emails(self, response):
        # Busca en texto y en hrefs (por si hay mailto:)
        text = response.text or ""
        hrefs = " ".join(response.css("a::attr(href)").getall())
        raw = set(EMAIL_RE.findall(text + " " + hrefs))
        # Filtrado básico de cosas raras
        return sorted({e.strip() for e in raw if len(e) <= 254})
