# -*- coding: utf-8 -*-
import scrapy
from ArticleSpider.util.zhihu_login import ZhiHu
from urllib import parse
import re
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem
from http import cookiejar  # 用于保存登陆的cookie
import json
import datetime
import os


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/topic']

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
    # zhihu = ZhiHu()
    # cookies = zhihu.read_cookie2login()
    cookies1 = {
        '_xsrf': 'RyIzCwCrj6TObcJpWwhUR3okEttFmjsL',
        "capsion_ticket": "\"2|1:0|10:1555165495|14:capsion_ticket|44:ZjVmMDBkZTEwZGQzNDIxZmFjN2ZkMjkzN2UwZDU1ODQ="
                          "|70ab4a64cdabda0e5bd3f9f0660247cdfb21b64689d01ee85c9c5a19a5c53b3e\"",
        "q_c1": "c5b7aa40e6e74378b180a09e06fad1e5|1555165647000|1555165647000",
        "z_c0": "\"2|1:0|10:1555165503|4:z_c0|80:MS4xYTJrc0FnQUFBQUFtQUFBQVlBSlZUVDhfbjEzQzlBa2dFaHhnM3"
                "A1Q0c3SDJkUnl0dHhwR0NnPT0=|7eee7231623713bd4724434810c0f4b9531b93e5882f66d072034a3dbd3c7350\"",
        "tgw_l7_route": "7bacb9af7224ed68945ce419f4dea76d"
    }

    # t = cookies._cookies['.zhihu.com']['/']
    # t.update(cookies._cookies['www.zhihu.com']['/'])
    # cookies = cookiejar.LWPCookieJar('cookie.txt')

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+)).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question,
                                     cookies=self.cookies1)

    def parse_question(self, response):

        match_obj = re.match("(.*zhihu.com/question/(\d+)).*", response.url)
        question_id = 0
        if match_obj:
            question_id = int(match_obj.group(2))
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", ".QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("question_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText>span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-Comment>button::text")
        item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()
        if int(question_id) == 315387406:
            s = question_item["answer_num"]
        question_item["click_num"] = question_item["watch_user_num"][1]
        question_item["watch_user_num"] = question_item["watch_user_num"][0]

        yield scrapy.Request(url=self.answer_start_url.format(question_id, 5, 0), headers=self.headers,
                             cookies=self.cookies1, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        for answer_data in answer_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["answer_id"] = answer_data["id"]
            answer_item["url"] = answer_data["url"]
            answer_item["question_id"] = answer_data["question"]["id"]
            answer_item["question_title"] = answer_data["question"]["title"]
            answer_item["author_id"] = answer_data["author"]["id"] if "id" in answer_data["author"] else None
            answer_item["content"] = answer_data["content"] if "content" in answer_data else None
            answer_item["praise_num"] = answer_data["voteup_count"]
            answer_item["comments_num"] = answer_data["comment_count"]
            answer_item["create_time"] = answer_data["created_time"]
            answer_item["update_time"] = answer_data["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            # yield answer_item
        if not answer_json["paging"]['is_end']:
            yield scrapy.Request(url=answer_json["paging"]['next'], headers=self.headers,
                                 cookies=self.cookies1, callback=self.parse_answer)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, headers=self.headers, cookies=self.cookies1)
