# -*- coding: utf-8 -*-
import scrapy
from ArticleSpider.items import CliuItem
from urllib import parse
import re


class AsiansisterSpider(scrapy.Spider):
    name = 'asiansister'
    allowed_domains = ['asiansister.com']
    start_url = 'https://asiansister.com/_page{0}'
    start_urls = [start_url.format(1)]

    def parse(self, response):
        page_list = response.css(".row .col-lg-4")
        for page_item in page_list:
            page_url = parse.urljoin(response.url, page_item.css(" center a::attr(href)").extract()[0])
            yield scrapy.Request(url=page_url, callback=self.parse_detail)
        match = re.match(".*?(\d+)$", response.url)
        page_num = '1'
        if match:
            page_num = match.group(1)
        is_last = response.css(".btn.page.disabled b::text").extract()[0]

        print(page_num+":complete")
        if is_last != '71':
            print(str(int(page_num)+1)+":start")
            yield scrapy.Request(url=self.start_url.format(int(page_num) + 1), callback=self.parse)

    def parse_detail(self, response):
        asItem = CliuItem()
        asItem["title"] = response.css(".container>center>h1::text").extract()[0]
        urls = response.css(".row>.col-lg-12>.showMiniImage::attr(dataurl)").extract()
        asItem["img_url"] = [parse.urljoin(response.url, url.replace("imageimages", "images")) for url in urls]
        asItem["dir_name"] = "asiansister"
        yield asItem
