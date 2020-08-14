from analysis_methods import statistics_method
import tushare as ts
import datetime

if __name__ == "__main__":
    time = "2020-07-30"
    print(time)
    t1 = datetime.datetime.strptime(time,"%Y-%m-%d")
    t2 = datetime.timedelta(6)
    t2 = t1-t2

    today_all = ts.get_day_all(time)
    res = statistics_method.statistics_10(today_all)

    first10 = []
    second10 = []
    for i in res:
        try:
            a = ts.get_hist_data(code = i[0], start=datetime.datetime.strftime(t2,"%Y-%m-%d"),end=time)["p_change"].values
            print(i,a)

            if sum(a>9.9) == 1:
                first10.append((i,a))
            if sum(a>9.9) == 2 and a[0]> 9.9 and a[1]>9.9:
                second10.append((i, a))
        except:
            continue
    f = open("1.txt", "w")
    for index,i in enumerate(first10):
        print(index,"-最后选择第一次涨停板：",i)
        f.writelines(i[0][0]+"\n")
    f.close()

    print("-----------------------最后选择两连板--------------------------")
    f = open("2.txt", "w")
    for index,i in enumerate(second10):
        print(index,"--最后选择两连板：",i)
        f.writelines(i[0][0]+"\n")
    f.close()

