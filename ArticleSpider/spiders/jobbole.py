# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobboleArticleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']
    pages = 5

    def parse(self, response):
        # post_urls = response.xpath('//*[@class="archive-title"]/@href').extract()
        post_nodes = response.xpath('//*[@class="post-thumb"]')
        for post_node in post_nodes:
            post_url = post_node.css("::attr(href)").extract()[0]
            img_url = post_node.css("img::attr(src)").extract()
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_img_url": img_url},
                          callback=self.parse_detail)
        next_url = response.css(".next.page-numbers::attr(href)").extract()[0]
        if next_url and self.pages > 0:
            self.pages -= 1
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):

        jobboleItem = JobboleArticleItem()

        jobboleItem["title"] = response.xpath('//*[@class="entry-header"]/h1/text()')[0].extract()
        jobboleItem["time"] = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].replace('·',
                                                                                                                    '').strip()
        jobboleItem["vote"] = response.xpath('//*[@class="post-adds"]/span[1]/h10/text()').extract()[0]
        jobboleItem["url"] = response.url
        jobboleItem["img_url"] = response.meta["front_img_url"]
        # print("title = \"" + jobboleItem["title"] + "\"  time=\"" + jobboleItem["time"] + "\"\n")
        yield jobboleItem
