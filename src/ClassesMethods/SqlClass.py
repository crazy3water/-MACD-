from sqlalchemy import create_engine
import pandas as pd

class Sql(object):
    def __init__(self,database):
        #"about_stocks"
        self.conn = create_engine("mysql+pymysql://root:root@localhost:3306/{}".format(database))

    def create_table(self, table_name):
        sql_drop_table = "drop table if exists {}".format(table_name)
        sql_create_table = "create table {}(stock_code char(10),concepts char(200))".format(table_name)

        self.conn.execute(sql_drop_table)
        self.conn.execute(sql_create_table)

    def show_table_colname(self,table_name):
        return pd.read_sql("desc {}".format(table_name),con=self.conn)

    def get_table(self,col_name,table_name):
        '''
        获得数据库中表中指定数据
        :param col_name: *为所有数据,列名字
        :param table_name:
        :return:
        '''
        sql_get_table = "select {} from {}".format(col_name,table_name)
        return pd.read_sql(sql_get_table,con = self.conn)