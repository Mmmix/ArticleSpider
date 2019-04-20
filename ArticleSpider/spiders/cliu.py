# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import CliuItem


class CliuSpider(scrapy.Spider):
    name = 'cliu'
    allowed_domains = ['t66y.com', 'cl.wpio.xyz', 'www.baidu.com']
    start_urls = ['https://cl.wpio.xyz/thread0806.php?fid=16']

    def parse(self, response):
        nodes = response.css(".tal h3 a")
        for node in nodes:
            if node.css("font::text").extract().__len__() == 0:
                title = node.css("::text").extract()[0]
            else:
                title = node.css("font::text").extract()[0]
            url = node.css("::attr(href)").extract()[0]

            if re.match(".*P]$", title):
                yield Request(url=parse.urljoin(response.url, url), meta={"title": title}, callback=self.parse_detail)

    def parse_detail(self, response):
        cliu_item = CliuItem()
        cliu_item["title"] = response.meta["title"]
        cliu_item["img_url"] = response.css(".tpc_content.do_not_catch input::attr(data-src)").extract()
        cliu_item["dir_name"] = "caoliu"
        yield cliu_item
