# coding:utf-8
import re
from time import sleep
import pandas as pd
import redis
from selenium import webdriver


class SinglePageParser:
    def __init__(self):
        self.pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.browser = webdriver.Safari()

    def url_download(self, url):
        try:
            if url is None:
                return None
            browser = self.browser
            browser.get(url)
            sleep(0.25)
            # 获取html
            html = browser.find_element_by_xpath("//*").get_attribute("outerHTML")
            # 去除html标签
            pre = re.compile('>(.*?)<')
            text = ''.join(pre.findall(html)).replace('&nbsp', '')
            # 确保为正确的标题
            html_title = browser.find_element_by_xpath('//*[@id="tdTitle"]/font[1]/b')\
                .text.replace(" ",  "") if browser.find_element_by_xpath(
                '//*[@id="tdTitle"]/font[1]/b') else ''
            if html_title == '':
                raise Exception("Invalid url!")
            # 某种判断
            if '一、' in text:
                project_number = re.search('编号：.*?、', text).group(0)\
                    .replace('编号：', '') if re.search('编号：.*?、', text) else ''
                # 特定数字
                contact_tel = re.search('0\d{2,3}-\d{7,8}|\(?0\d{2,3}[)-]?\d{7,8}|\(?0\d{2,3}[)-]*\d{7,8}', text).group(
                    0) if re.search('0\d{2,3}-\d{7,8}|\(?0\d{2,3}[)-]?\d{7,8}|\(?0\d{2,3}[)-]*\d{7,8}', text) else '-'
                this_result = {
                    '标题': html_title,
                    '来源': url}
                to_save_data = pd.DataFrame(this_result, index=[1])
                to_save_data.to_csv('./result.csv', header=False, index=False, mode='a+')
                print('ok')
            else:
                print('ok pas')
        except selenium.common.exceptions.NoSuchElementException:
            print("异常")


    def process_url(self):
        """
        获取一个未爬取的URL
        :return:
        """
        new_url = self.r.spop('todo-url')
        self.r.sadd('done-url', new_url)
        return new_url

    def has_new_url(self):
        """
        判断是否有未爬取的URL
        :return:
        """
        return self.new_url_size() != 0

    def new_url_size(self):
        """
        获取已知未爬取URL集合的大小
        :return:
        """
        return self.r.scard('todo-url')


if __name__ == "__main__":
    hd = HtmlDownloader()
    df = pd.DataFrame()
    data = pd.DataFrame({
        '标题': '标题',
        '来源': '来源'
    }, index=[1])
    data.to_csv('./result.csv', header=False, index=False, mode='a+')
    while hd.has_new_url():
        hd.url_download(hd.process_url())
        print(hd.new_url_size())
    hd.broser.quit()
