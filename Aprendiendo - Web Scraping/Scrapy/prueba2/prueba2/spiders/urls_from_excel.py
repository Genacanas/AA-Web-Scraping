import scrapy
import pandas as pd


class FromExcelSpider(scrapy.Spider):
    name = "from_excel"

    def __init__(
        self, excel_file=None, sheet_name=0, url_column="url", *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if not excel_file:
            raise ValueError("Pass -a excel_file=path.xlsx")

        df = pd.read_excel(
            excel_file, sheet_name=sheet_name
        )  # o pd.read_csv(...) si es CSV
        # Limpia nulos y espacios
        urls = df[url_column].dropna().astype(str).str.strip()
        # Opcional: filtra solo las que parecen http(s)
        self.start_urls = [u for u in urls if u.startswith(("http://", "https://"))]

    def parse(self, response):
        yield {"url": response.url, "title": response.css("title::text").get()}


"""
# Ejecución:
scrapy crawl from_excel -a excel_file="C:\ruta\mis_urls.xlsx" -a url_column="URL" -O salida.csv

"""
