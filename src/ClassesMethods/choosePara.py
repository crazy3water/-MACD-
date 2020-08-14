import talib
import tushare as ts
import datetime
import sys
import time
import tqdm
import numpy as np
from src.ClassesMethods.tosqlconcept import connect_sql

class ChoosePara(object):
    def __init__(self,delta=100,code=None,endTime=None,allDataFrame = None):
        self.buyPoint = -0.03
        self.sellPoint = 0.03
        self.BSdic = {1:"买入1",0:"卖出",2:"up++",3:"down--",4:"买入2",-1:"无状态"}
        self.canBuy = {}
        self.paraBS = {}
        talib.set_compatibility(1)
        if endTime == None:
            self.endTime = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            self.endTime = datetime.datetime.strptime(endTime,"%Y-%m-%d").strftime("%Y-%m-%d")
        self.detaTime = (datetime.datetime.strptime(endTime,"%Y-%m-%d") - datetime.timedelta(delta)).strftime("%Y-%m-%d")
        self.code = code
        self.allDataFrame = allDataFrame
        if code != None:
            self.codeHistPrice = ts.get_hist_data(code=code, start=self.detaTime, end=self.endTime)

        #连接sql 数据库
        self.conn = connect_sql()

    def dateDelta2str(self,dateTime,delta):
        timeStr = (datetime.datetime.strptime(dateTime,"%Y-%m-%d") - datetime.timedelta(delta)).strftime("%Y-%m-%d")
        return timeStr


    def getSingleCodeRealTimeByAPI(self,code):

        try:
            self.codeHistPrice = ts.get_realtime_quotes(code)
            codeHistClosePrice = "select closeHistPrice from stockprice where stock_code={}".format(code)
            codeHistClosePrice = self.conn.execute(codeHistClosePrice)

            for rowproxy in codeHistClosePrice:
                for column, value in rowproxy.items():
                    codeHistClosePrice = list(map(float,value.split(",")))
            # codeHistClosePrice = ts.get_hist_data(code=code, start=self.detaTime,
            #                                  end=(datetime.datetime.strptime(self.endTime,"%Y-%m-%d") - datetime.timedelta(1)).strftime("%Y-%m-%d"))["close"].values[::-1]
            self.code = code
            self.codeHistClosePrice =  list(codeHistClosePrice) + list(self.codeHistPrice["price"].values.astype(float))


            if len(self.codeHistClosePrice) > 30:
                if self.codeHistPrice["price"].values.astype(float) > 8:
                    return True
                else:
                    return False
            else:
                return False
        except:
            print("--")
            return False

    def getSingleCodeHistByAPI(self,code):
        #重新载入 单个的代码 获得历史价格  -- 排除新股
        self.codeHistPrice = ts.get_hist_data(code=code, start=self.detaTime, end=self.endTime)
        self.codeHistClosePrice = list(self.codeHistPrice["close"].values[::-1])
        self.code = code
        try:
            if len(self.codeHistPrice) > 30:
                return True
            else:
                return False
        except:
            return False

    def getSingleCodeSQLByAPI(self,code):
        # 配合数据库来写 ，数据库已经更新到当天收盘的最新价格了
        codeHistClosePrice = "select closeHistPrice from stockprice where stock_code={}".format(code)
        codeHistClosePrice = self.conn.execute(codeHistClosePrice)
        try:
            for rowproxy in codeHistClosePrice:
                for column, value in rowproxy.items():
                    codeHistClosePrice = list(map(float, value.split(",")))

            self.codeHistClosePrice = codeHistClosePrice
            self.code = code

            if len(self.codeHistClosePrice) > 30:
                return True
            else:
                return False
        except:
            return False


    def getCodeMACD(self):
        #获得MACD指标,模仿买入卖出点
        if self.code == None:
            print("getSingleCodeHistByAPI()方法获得code历史价格")
            sys.exit()
        priceClose = np.array(self.codeHistClosePrice)
        dif, dea, macd = talib.MACD(priceClose, fastperiod=12, slowperiod=26, signalperiod=9)

        trueMACD = (dif - dea) * 2
        self.paraBS["MACD"] = []

        volume = ts.get_k_data(code=code,start=self.dateDelta2str(self.endTime,10),end=self.endTime)["volume"].values
        # 卖出点
        if (trueMACD[-2]>0 and (trueMACD[-1]<trueMACD[-2] and trueMACD[-1]< self.sellPoint)):
            self.paraBS["MACD"].append(self.BSdic[0])
            return 0
        # 买入点1
        if (trueMACD[-2]<0 and trueMACD[-1]>trueMACD[-2] and self.buyPoint<trueMACD[-1] and trueMACD[-1]< 0 and dif[-1] > 0):
            self.paraBS["MACD"].append(self.BSdic[1])
            return 1

        # 买入点2 底部，放量
        if (trueMACD[-1]>trueMACD[-2] and trueMACD[-2]<trueMACD[-3] and trueMACD[-1] < 0 and volume[-1] > volume[-2]):
            self.paraBS["MACD"].append(self.BSdic[1])
            return 4

        if (trueMACD[-2]<0 and (trueMACD[-1]<trueMACD[-2] and self.buyPoint>trueMACD[-1])):
            self.paraBS["MACD"].append(self.BSdic[2])
            return 2

        if (trueMACD[-2]>0 and (trueMACD[-1]>trueMACD[-2] and self.buyPoint<trueMACD[-1])):
            self.paraBS["MACD"].append(self.BSdic[3])
            return 3

        return -1

    def getCodeKDJ(self):
        if self.code == None:
            print("getSingleCodeHistByAPI()方法获得code历史价格")
            sys.exit()
        K,D = talib.STOCH(
            self.codeHistPrice['high'].values,
            self.codeHistPrice['low'].values,
            self.codeHistPrice['close'].values,
            fastk_period=9,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0)

        J = list(map(lambda x,y: 3*x-2*y, K, D))


    def getCodeRSI(self):
        if self.code == None:
            print("请先调用getCodeHist()方法获得code历史价格")
            sys.exit()
        RSI6 = talib.RSI(self.codeHistPrice["close"], timeperiod=6)
        RSI12 = talib.RSI(self.codeHistPrice["close"], timeperiod=12)
        RSI24 = talib.RSI(self.codeHistPrice["close"], timeperiod=24)

    # def toCsv(self):



if __name__ == "__main__":
    # 时间为收盘时间
    Stime = "2020-08-13" #选择上一个交易日，因为使用实时预测是将今天的实时价格进行拼接计算的，如果收盘了就用收盘价格进行拼接了
    startClock = time.time()
    nowClock = time.time()

    today_all = ts.get_day_all()
    choosePara = ChoosePara(endTime=Stime,allDataFrame=today_all)

    fBuy1 = open("../BuyMACD接近交叉.txt", 'w')
    fBuy2 = open("../BuyMACD梯度为0.txt", 'w')

    jd = tqdm.tqdm(total=len(today_all["code"]))
    print(len(today_all["code"]),len(today_all["name"]))

    for index in range(len(today_all["code"])):
        code,name = today_all["code"][index],today_all["name"][index]
        if ((name[:2] != "ST") & (name[:3] != "*ST")):
            # if choosePara.getSingleCodeRealTimeByAPI(code):
            # if choosePara.getSingleCodeHistByAPI(code):
            if choosePara.getSingleCodeSQLByAPI(code):
                flag = choosePara.BSdic[choosePara.getCodeMACD()]
                if flag == "买入1":
                    fBuy1.write(code+'\n')
                    # print(name,":",code,"-",flag,"--",choosePara.paraBS)
                if flag == "买入2":
                    fBuy2.write(code + '\n')
            # time.sleep(0.1)
        jd.update(1)
        # print(index)
    fBuy1.close()
    fBuy2.close()
    sys.exit()
            # choosePara.getCodeKDJ()
            # choosePara.getCodeKDJ()