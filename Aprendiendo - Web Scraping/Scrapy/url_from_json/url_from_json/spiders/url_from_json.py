import scrapy, json


class FromJsonSpider(scrapy.Spider):
    name = "from_json"

    def __init__(self, json_file=None, key="urls", *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.start_urls = data[key]

    def parse(self, response):
        yield {"url": response.url, "title": response.css("title::text").get()}


"""
# Ejecución:
scrapy crawl from_json -a json_file="urls.json" -a key="urls" -O salida.csv

"""
