import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="py_spider", charset="utf8")
cursor = conn.cursor()

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                  "73.0.3683.103 Safari/537.36"
}


def crawl_ips():
    request_url = "https://www.xicidaili.com/nn/"

    re = requests.get(url=request_url, headers=header)
    selector = Selector(text=re.text)
    tr_list = selector.css("#ip_list tr")
    # ip_list = []
    for tr_item in tr_list[1:]:
        speed = tr_item.css(".bar::attr(title)").extract()[0]
        if speed:
            speed = float(speed.split("秒")[0])
        data_list = tr_item.css("td::text").extract()
        ip = data_list[0]
        port = data_list[1]
        proxy_type = data_list[5]
        # ip_list.append((ip, port, proxy_type, speed))
        print(ip + "," + port + "," + proxy_type + "," + str(speed))
        if junge_ip(ip, port, proxy_type):
            cursor.execute(
                'insert into proxy_id(ip,port,speed,proxy_type) VALUES ("{0}","{1}",{2},"{3}")'.format(ip, port, speed,
                                                                                                       proxy_type)
            )
            conn.commit()


def get_ip():
    random_sql = "select ip,port,proxy_type from proxy_ip ORDER BY RAND() LIMIT 1"
    cursor.execute(random_sql)
    for ip_info in cursor.fetchall():
        ip = ip_info[0]
        port = ip_info[1]
        proxy_type = ip_info[2]
        if junge_ip(ip, port, proxy_type):
            return "{0}://{1}:{2}".format(proxy_type, ip, port)


def junge_ip(ip, port, proxy_type):
    http_url = "http://www.baidu.com"
    proxy_url = "{0}://{1}:{2}".format(proxy_type, ip, port)
    if proxy_type == "HTTP":
        proxy_dict = {
            "http": proxy_url
        }
    else:
        proxy_dict = {
            "https": proxy_url
        }
    try:
        res = requests.get(http_url, headers=header, proxies=proxy_dict)
        code = res.status_code
        if code < 200 or code >= 300:
            print("invalid ip and port:" + ip + ":" + port)
            return False
    except Exception as e:
        print("invalid ip and port:" + ip + ":" + port)
        return False
    else:
        print("" + str(code) + ":" + ip + ":" + port)
        return True


if __name__ == "__main__":
    crawl_ips()
    # print(junge_ip("110.73.42.165", "8123", "HTTPS"))
