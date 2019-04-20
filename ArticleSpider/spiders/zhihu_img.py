# -*- coding: utf-8 -*-
import scrapy
import json
import re
from pyquery import PyQuery as pq
from ArticleSpider.items import CliuItem


class ZhihuImgSpider(scrapy.Spider):
    name = 'zhihu_img'
    allowed_domains = ['www.zhihu.com']
    start_urls = [
        'https://www.zhihu.com/api/v4/members/kong-hai-mo/following-questions?include=data%5B*%5D.created%2Canswer_count%2Cfollower_count%2Cauthor&offset=80&limit=20']

    answer_start_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_" \
                       "closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccoll" \
                       "apse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Cconten" \
                       "t%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_ti" \
                       "me%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_auth" \
                       "orized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_inf" \
                       "o%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2" \
                       "A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                      '73.0.3683.103 Safari/537.36',
        'x-zse-83': '3_1.1',
        'content-type': 'application/x-www-form-urlencoded'
    }

    cookies1 = {
        '_xsrf': 'RyIzCwCrj6TObcJpWwhUR3okEttFmjsL',
        "capsion_ticket": "\"2|1:0|10:1555165495|14:capsion_ticket|44:ZjVmMDBkZTEwZGQzNDIxZmFjN2ZkMjkzN2UwZDU1ODQ="
                          "|70ab4a64cdabda0e5bd3f9f0660247cdfb21b64689d01ee85c9c5a19a5c53b3e\"",
        "q_c1": "c5b7aa40e6e74378b180a09e06fad1e5|1555165647000|1555165647000",
        "z_c0": "\"2|1:0|10:1555165503|4:z_c0|80:MS4xYTJrc0FnQUFBQUFtQUFBQVlBSlZUVDhfbjEzQzlBa2dFaHhnM3"
                "A1Q0c3SDJkUnl0dHhwR0NnPT0=|7eee7231623713bd4724434810c0f4b9531b93e5882f66d072034a3dbd3c7350\"",
        "tgw_l7_route": "7bacb9af7224ed68945ce419f4dea76d"
    }

    def parse(self, response):
        question_json = json.loads(response.text)
        yield scrapy.Request(url=self.answer_start_url.format(22856657, 5, 0), headers=self.headers,
                             cookies=self.cookies1, callback=self.parse_answer)
        # for question in question_json["data"]:
        #     question_id = question["id"]
        #     if question["follower_count"] > 5000:
        #         yield scrapy.Request(url=self.answer_start_url.format(question_id, 5, 0), headers=self.headers,
        #                              cookies=self.cookies1, callback=self.parse_answer)
        # if not question_json["paging"]["is_end"]:
        #     yield scrapy.Request(url=question_json["paging"]["next"], headers=self.headers, cookies=self.cookies1,
        #                          callback=self.parse)

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        for answer in answer_json["data"]:
            content = answer["content"]
            doc = pq(content)
            imgs_doc = doc('img')
            img_urls = []
            for img_doc in imgs_doc:
                pq_url = pq(img_doc)
                url = pq_url.attr('src')
                if re.match("^http", url):
                    img_urls.append(url)
            zhihu_item = CliuItem()
            zhihu_item["title"] = answer["question"]["title"]
            zhihu_item["img_url"] = img_urls
            zhihu_item["dir_name"] = "zhihu_img"
            yield zhihu_item
        if not answer_json["paging"]["is_end"]:
            yield scrapy.Request(url=answer_json["paging"]["next"], headers=self.headers, cookies=self.cookies1,
                                 callback=self.parse_answer)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, headers=self.headers, cookies=self.cookies1)
