import pandas as pd
import numpy as np
import os
import pymysql
from GetData import dataAll
from tqdm import tqdm

def connect_db(database):
    host = "investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com"
    port = 3306
    username = "someone555"
    database = database
    password = "12345asdfg"
    try:
        con = pymysql.connect(host=host, user=username, password=password,
                db=database, charset='utf8') # 한글처리 (charset = 'utf8')
    except Exception as e:
        print(">> connection 실패 ",e)
        return False

    return con

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

def FindIndices(df_list):
    minDate = min([df_list[i].index[0] for i in range(len(df_list))])
    maxDate = max([df_list[i].index[-1] for i in range(len(df_list))])
    date_range = pd.date_range(minDate, maxDate)
    resultdf = pd.DataFrame({'날짜': date_range})
    resultdf = resultdf.set_index("날짜")
    resultdf["날짜"] = resultdf.index
    resultdf = resultdf.drop_duplicates()
    Industry_Price_Index = []
    for i in tqdm(range(len(resultdf))):
        curr_date = resultdf.iloc[i]["날짜"]
        total_curr_price_c = 0
        total_curr_price_o = 0
        total_curr_price_h = 0
        total_curr_price_l = 0
        cnt = 0
        total_curr_market = 0
        for j in range(len(df_list)):
            try:
                # print(curr_date)
                curr_price_c = df_list[j].loc[curr_date]["Close"]
                curr_market = df_list[j].loc[curr_date]["시가총액"]

                curr_price_o = df_list[j].loc[curr_date]["Open"]
                curr_price_h = df_list[j].loc[curr_date]["High"]
                curr_price_l = df_list[j].loc[curr_date]["Low"]

            except Exception as e:
                # print(e)
                continue
            # if curr_market == np.NaN:
            #     curr_market = np.mean(df_list[j]["시가총액"].dropna().tolist())
            total_curr_market += curr_market
            total_curr_price_c += curr_price_c * curr_market
            total_curr_price_o += curr_price_o * curr_market
            total_curr_price_h += curr_price_h * curr_market
            total_curr_price_l += curr_price_l * curr_market
            cnt+=1
        if cnt == 0:
            continue
        open = total_curr_price_o/total_curr_market
        close = total_curr_price_c/total_curr_market
        high = total_curr_price_h/total_curr_market
        low = total_curr_price_l/total_curr_market
        Industry_Price_Index.append([curr_date, open,high,close,low])

    resultData = pd.DataFrame(Industry_Price_Index,columns=["date","open","high","close","low"])
    resultData["open"] = resultData["open"].astype("float64")
    resultData["high"] = resultData["high"].astype("float64")
    resultData["close"] = resultData["close"].astype("float64")
    resultData["low"] = resultData["low"].astype("float64")
    resultData["date"] = resultData["date"].astype("datetime64")
    resultData = resultData.set_index("date")
    return resultData

def getIndicator(categoryName):
    stockList = []
    tabels = getTableName(categoryName)
    for i in tqdm(range(len(tabels))):
        curr_name = tabels[i]
        try:
            curr_data = dataAll(categoryName,curr_name)
            curr_M = dataAll(categoryName+"M",curr_name)
            curr_data = curr_data[~curr_data.index.duplicated(keep='first')]
            curr_M = curr_M[~curr_M.index.duplicated(keep='first')]
            conData = pd.concat([curr_data, curr_M["시가총액"]], axis=1, join='outer').dropna().set_index("timestamp")
            conData = conData.loc[~conData.index.duplicated(keep='first')]
            stockList.append(conData)
        except Exception as e:
            print(e)
            pass
    resultData = FindIndices(stockList)
    return resultData


import pandas as pd
import pymysql
import os
from sqlalchemy import create_engine
import sqlalchemy

def getDatabaseName():
    host = "investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com"
    port = 3306
    username = "someone555"
    password = "12345asdfg"
    con = pymysql.connect(
        host=host,
        user=username,
        password=password,
        database='information_schema'  # information_schema 데이터베이스에 접속하여 데이터베이스 목록을 가져옵니다.
    )

    # 커서 생성
    cursor = con.cursor()

    # 데이터베이스 목록 조회
    cursor.execute("SHOW DATABASES")

    # 결과 가져오기
    databases = cursor.fetchall()
    databaseName = [i[0] for i in databases]
    cursor.close()
    con.close()
    return databaseName
def connect_db(database):
    host = "investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com"
    port = 3306
    username = "someone555"
    database = database
    password = "12345asdfg"
    try:
        con = pymysql.connect(host=host, user=username, password=password,
                db=database, charset='utf8') # 한글처리 (charset = 'utf8')
    except Exception as e:
        print(">> connection 실패 ",e)
        return False

    return con
def connect():
    host = "investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com"
    port = 3306
    username = "someone555"
    password = "12345asdfg"
    try:
        con = pymysql.connect(host=host, user=username, password=password, charset='utf8') # 한글처리 (charset = 'utf8')
    except Exception as e:
        print(">> connection 실패 ",e)
        return False

    return con

def CreateDB(database_name):
    # 데이터베이스 생성 SQL 쿼리
    con = connect()
    create_database_query = f"CREATE DATABASE {database_name}"

    try:
        # 커서 생성
        cursor = con.cursor()

        # 데이터베이스 생성 쿼리 실행
        cursor.execute(create_database_query)

        # 변경 내용 커밋
        con.commit()
        print(f"데이터베이스 '{database_name}'가 생성되었습니다.")
        cursor.close()
        con.close()

    except Exception as e:
        # 오류 발생 시 롤백
        con.rollback()
        print(f"데이터베이스 생성 중 오류 발생: {e}")
        cursor.close()
        con.close()

def Create_db_table(name,database_name):
    # STEP 2: MySQL Connection 연결
    try:
        con = connect_db(database_name)
    except Exception as e:
        print(">> connection 실패 ",e)
        return False
    # STEP 3: Connection 으로부터 Cursor 생성
    cur = con.cursor()
    sql = '''CREATE TABLE '''+ name.replace('/','_')+'''(
            timestamp datetime,
            open float(32),
            high float(32),
            low float(32),
            close float(32)
            )
    '''
    try:
        cur.execute(sql) # sql문  실행
        print(">> "+name.replace('/','_')+" 테이블 생성 성공!")
        cur.close()
        con.close()
    except pymysql.err.OperationalError:
        print(">> 테이블 생성 실패 : 이미 생성된 테이블입니다.")
        cur.close()
        con.close()
        return False
    except pymysql.err.ProgrammingError:
        print(">> 테이블 생성 실패 : sql문 에러입니다.")
        cur.close()
        con.close()
        return False
    return True

def Insert_db_table(df,name,database_name):
    try:
        db_connection_str = "mysql+pymysql://someone555:12345asdfg@investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com/"+database_name
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()
    except Exception as e:
        print(">> connection 실패 ",e)
        return df
    df['timestamp'] = df.index
    dtypesql = {"timestamp":sqlalchemy.types.DateTime(), 
            'open':sqlalchemy.types.Float(32), 
            'high':sqlalchemy.types.Float(32),
            'low':sqlalchemy.types.Float(32),
            'close':sqlalchemy.types.Float(32),
    }
    print(">> 데이터베이스에 데이터 업로드 시작")
    try:
        df.to_sql(name = name.replace('/','_'),con = conn,if_exists='append',index=False,dtype = dtypesql)
        print(">> 데이터 업로드 성공!")
        conn.close()
        return True
    except Exception as e:
        print(">> 데이터 업로드 실패... 파라미터를 확인하세요",e)
        conn.close()
        return df
    
def FinanceData():
    cate = list(pd.read_csv("category.csv",index_col=0).index)
    database = getDatabaseName()

    if not "categoryIndicator" in database:
        CreateDB("categoryIndicator")

    tableList = getTableName("categoryIndicator")
    for i in range(len(cate)):
        curr_name = cate[i]
        curr_M = cate[i]+"M"
        if curr_name == "담배" and curr_name == "사무용전자제품":
            continue
        if curr_name in database and curr_M in database:
            
            if not curr_name in tableList:
                Create_db_table(curr_name,"categoryIndicator")
                data = getIndicator(curr_name)
                Insert_db_table(data,curr_name,"categoryIndicator")
            else:
                pass
                # data = getIndicator(curr_name)
                # Insert_db_table(data,curr_name,"categoryIndicator")

FinanceData()