import scrapy
from scrapy_playwright.page import PageMethod


class ContactSpider(scrapy.Spider):
    name = "playwright_logic"
    start_urls = ["https://bucco.com.ar/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        # espera a que no haya requests de red por un rato
                        PageMethod("wait_for_load_state", "networkidle"),
                        # si necesitas hacer scroll para cargar contenido:
                        # PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        # PageMethod("wait_for_timeout", 1000),
                    ],
                },
            )

    def parse(self, response):
        # A esta altura 'response' ya contiene el HTML renderizado por Playwright
        emails = response.css('a[href^="mailto:"]::attr(href)').getall()
        for e in emails:
            yield {"email": e.replace("mailto:", "").strip(), "url": response.url}

        if emails:
            return  # si encontró emails, no sigue a /contacto
        
        # Si no encontró emails, busca enlaces de contacto
        