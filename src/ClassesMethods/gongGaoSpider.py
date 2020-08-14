import urllib3
import time
from lxml import etree
import re
from tqdm import tqdm
import datetime


class GongGaoSpider(object):
    '''
    查找公告中的关键词
    '''
    def __init__(self,startSpiderTime=None,month=None,day=None,keyWords=None):
        '''
        :param startSpiderTime: 公告开始时间 默认为当天
        :param month:           公告结束时间 默认为前一天，month-day
        :param day:
        :param keyWords:        公告中包含的关键词
        '''
        self.keyWords = keyWords
        self.endSpiderIndex = 0
        self.endSpiderIndexNum = 100
        self.endSpiderFlag = 0
        if startSpiderTime == None:
            self.startSpiderTime = datetime.datetime.now().strftime("%m-%d")
        else:
            self.startSpiderTime = startSpiderTime
        if month == None:
            self.endSpiderTime = datetime.datetime.now() - datetime.timedelta(1)
        else:
            self.endSpiderTime = datetime.datetime(year= int(datetime.datetime.now().strftime("%Y")),month= month,day= day)

    def findKeyWords(self,content,publishTime):
        y = publishTime.split("-")[0]
        m = publishTime.split("-")[1]
        d = publishTime.split("-")[2]
        if self.endSpiderTime - datetime.datetime(year=int(y), month=int(m), day=int(d)) >= datetime.timedelta(0):
            self.endSpiderIndex += 1
            if self.endSpiderIndex > self.endSpiderIndexNum:
                self.endSpiderFlag = 1
        for keyWord in self.keyWords:
            if re.search(pattern=keyWord,string=content):
                print(content+"--"+publishTime)

    def getContentsInPages(self,startpages,endpages):
        for page in tqdm(range(startpages,endpages),ncols=100):
            url_ = "http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?page_index={}".format(page)
            http = urllib3.PoolManager()
            req = http.request("GET",url_).data

            html = etree.HTML(req)

            # html = etree.tostring(html).decode('utf-8')

            html_data = html.xpath('//table[@class="body_table"]/tbody/tr')
            contents = html_data[0].xpath('//th/a[@target="_blank"]/text()')
            times = html_data[0].xpath('//td[@width="80"]/text()')

            for i in range(0,int(len(contents)/2),2):
                self.findKeyWords(contents[i],times[i])
            if self.endSpiderFlag:
                break
            time.sleep(0.5)

if __name__ == "__main__":
    # print(datetime.datetime.strptime("01-01","%m-%d"))
    gongGaoSpider = GongGaoSpider(keyWords = ['回购'])
    gongGaoSpider.getContentsInPages(startpages=1,endpages=100)