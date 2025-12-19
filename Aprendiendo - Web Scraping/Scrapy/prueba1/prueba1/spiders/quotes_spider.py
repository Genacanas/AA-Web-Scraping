import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        # recorrer cada bloque de quote
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
            }
