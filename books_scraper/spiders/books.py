import scrapy
import wordtodigits

from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        # "h3 a::attr(href)" == "h3 > a::attr(href)"
        # book_urls = response.css(".product_pod > a::attr(href)").getall()
        book_urls = response.css("h3 a::attr(href)").getall()

        for book_url in book_urls:
            yield response.follow(book_url, callback=self.parse_single_book)

        # next_page = response.css(".pager > li.next > a::attr(href)").get()
        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_single_book(response: Response) -> None:
        yield {
                "title": response.css(".product_main > h1::text").get(),
                "price": float(
                    response.css(".price_color::text").get().replace("£", "")
                ),
                "amount_in_stock":  int(
                    response.css(".instock").get().replace("(", "").split()[-3]
                ),
                "rating": int(wordtodigits.convert(
                    response.css("p.star-rating::attr(class)").get().split()[-1]
                )),
                "category": response.css(
                    ".breadcrumb > li:nth-child(3) > a::text"
                ).get(),
                "description": response.css(".product_page > p::text").get(),
                "upc": response.css("tr:nth-of-type(1) td::text").get(),
            }
