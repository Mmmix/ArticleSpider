# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from ArticleSpider.util.common import get_nums
import datetime


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    time = scrapy.Field()
    url = scrapy.Field()
    vote = scrapy.Field()
    img_url = scrapy.Field()


class CliuItem(scrapy.Item):
    title = scrapy.Field()
    dir_name = scrapy.Field()
    img_url = scrapy.Field()


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题item
    question_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
insert into zhihu_question(question_id,topics,url,title,content,answer_num,comments_num,watch_user_num,
click_num,crawl_time)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE content=VALUES(content),title=VALUES(title),answer_num=VALUES(answer_num),comments_num=
VALUES(comments_num),watch_user_num=VALUES(watch_user_num),click_num=VALUES(click_num),crawl_time=VALUES(crawl_time)
 """

        question_id = self["question_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = self["title"][0]
        content = self["content"][0]
        answer_num = get_nums("".join(self["answer_num"]).replace(",", ""))
        comments_num = get_nums("".join(self["comments_num"]).replace(",", ""))
        watch_user_num = get_nums("".join(self["watch_user_num"]).replace(",", ""))
        click_num = get_nums("".join(self["click_num"]).replace(",", ""))
        crawl_time = datetime.datetime.now()

        params = (question_id, topics, url, title, content, answer_num, comments_num, watch_user_num,
                  click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    answer_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    question_title = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
insert into 
zhihu_answer(answer_id,url,question_id,question_title,author_id
,content,praise_num,comments_num,create_time,update_time,crawl_time) 
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
on DUPLICATE key UPDATE  content=VALUES (content),praise_num=VALUES (praise_num),comments_num=VALUES (comments_num),
update_time=VALUES (update_time)
"""

        create_time = datetime.datetime.fromtimestamp(self["create_time"])
        update_time = datetime.datetime.fromtimestamp(self["update_time"])

        params = (self["answer_id"], self["url"], self["question_id"], self["question_title"],
                  self["author_id"], self["content"], self["praise_num"], self["comments_num"]
                  , create_time, update_time, self["crawl_time"])
        return insert_sql, params
