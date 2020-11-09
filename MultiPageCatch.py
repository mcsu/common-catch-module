# coding:utf-8
from time import sleep
import redis
from selenium import webdriver

class MultiPageCatch:  # 只负责抓取项目名称与项目地址 k-v name-address
    def __init__(self):  # 初始化redis 存储抓取进度
        print("init redis")
        self.pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def url_download(self, url):  # 下载url的源码
        try:
            if url is None:
                return None
            browser = webdriver.Safari()
            browser.get(url)
            html = browser.find_element_by_xpath("//*").get_attribute("outerHTML")
            title = BeautifulSoup(html, 'html.parser').title
            # 包含正确的title关键词
            if str(title).strip() == "<title>xxxx网</title>":
                browser.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[2]/a[12]/img').click()
                # 确定页码数， 每页项目数
                for p in range(67):
                    for i in range(20):
                        # 按需确定xpath
                        print('第{}页第{}项'
                              .format(browser
                                      .find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]/b').text, i+1))
                        html_text = browser.find_element_by_xpath(
                            '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[' + str(i + 1) +
                            ']/td[2]/a').text
                        html_href = browser.find_element_by_xpath(
                            '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[' + str(i + 1) +
                            ']/td[2]/a').get_attribute('href')
                        # k-v text-href
                        # to-url
                        # 标题判断
                        if '公告' not  in html_text:
                            # 使用redis存储
                            self.r.sadd('todo-url', html_href)
                            self.r.set(html_text, html_href)
                            print('ok')
                        else:
                            print(html_text)
                    # 翻页
                    page_xpath = ''
                    if 67 - p <= 67:
                        page_xpath = '2'

                    browser.find_element_by_xpath(
                        '//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[2]/a['+page_xpath+']/img').click()
                        #//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[2]/a[11]/img
                    # 缓冲时间
                    sleep(0.5)
            return None
        except selenium.common.exceptions.InvalidArgumentException:
            print("URL异常")
            return None


if __name__ == "__main__":
    hd = HtmlDownloader()
    hd.url_download('http:domain.com')
