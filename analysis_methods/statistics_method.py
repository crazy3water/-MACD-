from src.ClassesMethods import SqlClass


def  statistics_10(today_all):
    # 涨跌停数量
    stock_10 = today_all[today_all['p_change'] > 9.9]
    stock_10 = stock_10[stock_10['p_change'] < 10.05]["code"]
    stock_r10 = today_all[today_all['p_change'] < -9.9]["code"]
    print("今日涨停数量>9.9：", len(stock_10))
    print("今日跌停数量<-9.9：", len(stock_r10))

    # 概念统计
    # 1.连接数据库提取代码对应概念
    sql = SqlClass.Sql("about_stocks")

    sql_concept_df = sql.get_table(col_name="*", table_name="stocks_list")
    sql_concept_df.index = sql_concept_df["stock_code"]

    del_concept = ["融资融券", "标普道琼斯A股", "深股通", "沪股通", "MSCI预期", "MSCI概念","新股与次新股","非科创次新股","央企国资改革","股权转让",""]
    concept_all_10 = []
    for code in stock_10:
        # if code[:3] != "688" and code[:3] != "300":
            for concept in sql_concept_df.loc[code].values[1].split('\t'):
                if concept not in del_concept:
                    concept_all_10 += [concept]


    # 2.统计涨停概念 -- 权重
    concept_dic = {}
    for concept in concept_all_10:
            if concept not in concept_dic.keys():
                concept_dic[concept] = 1 / len(stock_10)
            else:
                concept_dic[concept] += 1 / len(stock_10)

    print("涨停概念权重排序：")
    print(sorted(concept_dic.items(), key=lambda x: x[1], reverse=True))

    weight_10 = []
    for code in stock_10:
        if code[:3] != "688" and code[:3] != "300":
            weight = 0
            concept_all_10 = []
            for concept in sql_concept_df.loc[code].values[1].split('\t'):
                if concept not in del_concept:
                    concept_all_10 += [concept]
            for concept in concept_all_10:
                    weight += concept_dic[concept] / len(concept_all_10)
            weight_10.append((code, weight,concept_all_10))

    print("涨停股票权重排序：")
    res = sorted(weight_10, key=lambda x: x[1], reverse=True)

    return res
