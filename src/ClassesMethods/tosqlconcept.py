import pandas as pd
import tushare as ts
from sqlalchemy import create_engine
import urllib3
import time
from lxml import etree
import datetime
import tqdm

###########################################
'''
    这个.py文件用于获得当日股票(非“300” “688”)的概念
    概念来源：同花顺
                       数据库名字    |     表名
    数据存储位置：     about_stocks     stocks_list
    
    这个.py文件用于获得股票历史价格，并做每日更新
    概念来源：新浪
                       数据库名字    |     表名
    数据存储位置：     about_stocks     stockprice
'''
###########################################

def connect_sql():
    conn = create_engine("mysql+pymysql://root:root@localhost:3306/about_stocks")
    return conn

def create_table(conn,table_name):
    sql_drop_table = "drop table if exists {}".format(table_name)
    sql_create_table = "create table {}(stock_code char(10),concepts char(200))".format(table_name)

    conn.execute(sql_drop_table)
    conn.execute(sql_create_table)

def get_concept_spider(code):
    url_ = "http://stockpage.10jqka.com.cn/{}/".format(code)
    http = urllib3.PoolManager()
    req = http.request("GET",url_).data.decode('utf-8')
    html = etree.HTML(req)
    # html = etree.tostring(html).decode('utf-8')
    html_data = html.xpath('//div[@class="sub_cont_3"]/dl/dd/@title')[0].replace("，","\t")
    return html_data


def update_concept():
    print("更新股票代码-概念")
    # 用于保存 股票代码-概念  ：应该是一段时间就要更新一次
    df = pd.DataFrame()

    t1 = time.time()
    # sn(新浪)、tt(腾讯)、nt(网易)
    # 获得当日收盘所有股票
    today_all = ts.get_day_all()

    print(today_all.head())

    # 连接数据库
    conn = connect_sql()
    create_table(conn, "stocks_list")

    concept = []
    codes = []
    count = 0
    tjd = tqdm.tqdm(total=len(today_all['code'].values))
    # 从同花顺爬取code对应的概念
    for code in today_all['code'].values:
        # if code[:3] != "300" and code[:3] != "688":
        time.sleep(0.1)
        codes.append(code)
        concept.append(get_concept_spider(code))
        # print("完成注入股票:{}，概念为：{}".format(code, concept[-1]))
        tjd.update(1)

    df['stock_code'] = codes
    df['concepts'] = concept

    df.to_sql('stocks_list', conn, if_exists="replace", index=False)
    t2 = time.time()

    print("时间：", t2 - t1, " s")

def saveYesterdayClosePrice():
    '''
    当数据库中历史数据出现问题时，使用函数重新保存至最近交易日收盘：
    使用场景，第一次使用，或者数据库出错需要重新读入使用
    :return:
    '''
    #连接数据库
    conn = connect_sql()
    today_all = ts.get_day_all()

    count = 0
    codes = []
    closePrice = []
    volumePrice = []
    endTime = "2020-08-13" #到这个时间点之前（包括这天）的收盘价格
    detaTime = (datetime.datetime.strptime(endTime, "%Y-%m-%d") - datetime.timedelta(100)).strftime("%Y-%m-%d")
    tjd = tqdm.tqdm(total=len(today_all['code'].values))
    for code in today_all['code'].values:
        # if code[:3] != "300" and code[:3] != "688":
        codes.append(code)
        try:
            get_hist_data = ts.get_hist_data(code=code, start=detaTime,
                                                  end=(datetime.datetime.strptime(endTime,
                                                                                  "%Y-%m-%d") - datetime.timedelta(
                                                      0)).strftime("%Y-%m-%d"))
            codeHistClosePrice = get_hist_data["close"].values[::-1]

            codeHistVolumePrice = get_hist_data["volume"].values[::-1]

        except:
            codeHistClosePrice = []
            codeHistVolumePrice = []
        closePrice.append(",".join(list(map(str, codeHistClosePrice))))
        volumePrice.append(",".join(list(map(str, codeHistVolumePrice))))
        tjd.update(1)
    df = pd.DataFrame()
    df['stock_code'] = codes
    df['closeHistPrice'] = closePrice
    df['updatetime'] = endTime
    df["volume"] = volumePrice
    df.to_sql('stockprice', conn, if_exists="replace", index=False)
    pass

def isTradeDate():
    print(ts.is_holiday("2020-05-02"))


def updateSqlHistClosePrice():
    '''
    更新数据库成交数据 应该在
    :return:
    '''
    conn = connect_sql()
    # endTime = datetime.datetime.now().strftime("%Y-%m-%d")
    endTime = "2020-08-12"
    allCodeInSql = conn.execute("select stock_code,closeHistPrice from stockprice")

    histPrice = []
    stock_code = []
    print("*"*10+"导入{}收盘数据".format(endTime)+"*"*10)
    tq = tqdm.tqdm(total=3943)
    if ts.is_holiday(endTime) == False and ts.get_realtime_quotes("000001")["date"].values[0] == endTime:
        for codes in allCodeInSql:
            for key, values in codes.items():
                if key == "stock_code":
                    closePrice = ts.get_realtime_quotes(values)["price"].values
                    stock_code.append(values)
                if key == "closeHistPrice":
                    histPrice.append(values+","+str(closePrice[0]))
                    tq.update(1)
    df = pd.DataFrame()
    df['stock_code'] = stock_code
    df['closeHistPrice'] = histPrice
    df['updatetime'] = endTime
    df.to_sql('stockprice', conn, if_exists="replace", index=False)


if __name__ == "__main__":
    # update_concept()
    saveYesterdayClosePrice() #重新加载数据
    # updateSqlHistClosePrice()