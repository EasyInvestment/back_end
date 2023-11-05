import pymysql
import pandas as pd
import FinanceDataReader as fdr
from pykrx import stock
from datetime import datetime
def connect_db(database):
    host = "financedata.cyyrt9e5hsme.ap-northeast-2.rds.amazonaws.com"
    port = 3306
    username = "root"
    database = database
    password = "825582qaz"
    try:
        con = pymysql.connect(host=host, user=username, password=password,
                db=database, charset='utf8') # 한글처리 (charset = 'utf8')
    except Exception as e:
        print(">> connection 실패 ",e)
        return False

    return con

def dataAll(database,table):
    # 커서 생성
    con = connect_db(database)
    cursor = con.cursor()

    # 모든 데이터 가져오기
    cursor.execute("SELECT * FROM "+table)

    data = cursor.fetchall()

    column_names = [i[0] for i in cursor.description]

    df = pd.DataFrame(data, columns=column_names)

    # 연결 및 커서 닫기
    cursor.close()
    con.close()

    return df

def getTableName(database):
    con = connect_db(database)
    # 커서 생성
    cursor = con.cursor()

    # 테이블 목록 조회
    cursor.execute("SHOW TABLES")

    # 결과 가져오기
    tables = cursor.fetchall()
    tables = [table[0] for table in tables]
    cursor.close()
    con.close()

    return tables

# 카테고리의 주식 이름 목록 반환
def getStockList(name):
    # 한국거래소 상장종목 전체
    df_krx = fdr.StockListing('KRX')
    table = getTableName(name)
    table = [i.replace("s","") for i in table]
    curr_sym = []
    for i in range(len(table)):
        curr_sym.append(df_krx[df_krx["Symbol"] == table[i]]["Name"].values[0])
    
    return curr_sym

def subData(symbol):
    today = str(datetime.now())[:10].replace("-","")
    df = stock.get_market_fundamental(today, today, "005930")
    col = list(df.columns)
    dic = {}
    for name in col:
        dic[name] = df[name].values[0]

    return dic

def ChatGptData(name):
    df_krx = fdr.StockListing('KRX')
    table = getTableName(name)
    table = [i.replace("s","") for i in table]
    curr_category = name
    name = []
    sym = []
    for i in range(len(table)):
        sym.append(df_krx[df_krx["Symbol"] == table[i]]["Symbol"].values[0])
        name.append(df_krx[df_krx["Symbol"] == table[i]]["Name"].values[0])
    
    result = {}
    for i in range(len(sym)):

        curr_name = name[i]
        curr_sym = sym[i]
        temp = subData(curr_sym)

        result[name] = temp

    return result

