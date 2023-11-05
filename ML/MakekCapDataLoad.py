import FinanceDataReader as fdr
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import pymysql
import os
import chromedriver_autoinstall
from sqlalchemy import create_engine
import sqlalchemy
from pykrx import stock
from datetime import datetime

def chrome_driver():
    options = webdriver.ChromeOptions()
    chrome_ver = chromedriver_autoinstall.get_version()

    # mac
    chromedriver = f'{chrome_ver.split(".")[0]}/chromedriver'

    # window
    # chromedriver = f'{chrome_ver.split(".")[0]}/chromedriver.exe'
    
    if not os.path.exists(chromedriver):
        os.makedirs(os.path.dirname(chromedriver), exist_ok=True)
        res = chromedriver_autoinstall.install()
    driver = webdriver.Chrome(chromedriver, options=options)
    return driver

def getDatabaseName():
    host = "127.0.0.1"
    port = 3306
    username = "root"
    password = "825582qaz"
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

def getLastDate(database,table):

    con = connect_db(database)
    cursor = con.cursor()
    query = "SELECT * FROM "+ table +" ORDER BY timestamp DESC LIMIT 1"
    cursor.execute(query)
    last_row = cursor.fetchone()

    if last_row == None:
        return "2000-01-01"
    
    cursor.close()
    con.close()

    return str(last_row[-1])[:10]

def connect_db(database):
    host = "127.0.0.1"
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
def connect():
    host = "127.0.0.1"
    port = 3306
    username = "root"
    password = "825582qaz"
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
            시가총액 float(32),
            거래량 float(32),
            거래대금 float(32),
            상장주식수 float(32),
            timestamp datetime
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
    # except pymysql.err.ProgrammingError:
    #     print(">> 테이블 생성 실패 : sql문 에러입니다.")
    #     cur.close()
    #     con.close()
    #     return False
    return True

def Insert_db_table(df,name,database_name):
    try:
        db_connection_str = "mysql+pymysql://root:825582qaz@127.0.0.1/"+database_name
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()
    except Exception as e:
        print(">> connection 실패 ",e)
        return df
    df['timestamp'] = df.index
    dtypesql = {
            '시가총액':sqlalchemy.types.Float(32), 
            '거래량':sqlalchemy.types.Float(32),
            '거래대금':sqlalchemy.types.Float(32),
            '상장주식수':sqlalchemy.types.Float(32),
            "timestamp":sqlalchemy.types.DateTime(), 
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
    # 카테고리 수집
    # driver = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())
    # driver = chrome_driver()
    driver = webdriver.Chrome()
    driver.get("https://finance.naver.com/sise/sise_group.naver?type=upjong")

    sector = driver.find_elements(By.CSS_SELECTOR,"#contentarea_left > table > tbody > tr > td > a")
    sector_url = [curr.get_attribute("href") for curr in sector]
    sector_name = [curr.text.replace(",","") for curr in sector]

    # 주식 카테고리 별 이름 데이터
    category = []
    for i in range(len(sector_url)):
        driver.get(sector_url[i])
        sectorDetail = driver.find_elements(By.CSS_SELECTOR, "#contentarea > div:nth-child(5) > table > tbody > tr > td.name")
        companyName = [curr.text.replace("*","").replace(" ","").replace(",","") for curr in sectorDetail]

        category.append(companyName)

    data = pd.DataFrame(category)
    data["index"] = sector_name
    data = data.set_index("index")
    
    # 한국거래소 상장종목 전체
    df_krx = fdr.StockListing('KRX')
    today = str(datetime.now())[:10].replace("-","")
    for k in range(len(data)):
        curr_category = data.iloc[k].dropna().tolist()
        curr_name = data.index[k]
        curr_sym = []
        for i in range(1,len(curr_category)):
            try:
                curr_sym.append(df_krx[df_krx["Name"] == curr_category[i]]["Code"].values[0])
            except:
                pass
        curr_name = curr_name + "M"
        databaseName = getDatabaseName()
        if not curr_name in databaseName:
            CreateDB(curr_name)

        tableList = getTableName(curr_name)
        
        for i in range(len(curr_sym)):
            tabel_name = "s"+curr_sym[i]
            if not tabel_name in tableList:
                print(">>",curr_name,"카테고리에",tabel_name,"새로 만드는중...")
                Create_db_table(tabel_name,curr_name)
                df = stock.get_market_cap("20000101", today, str(curr_sym[i]))
                Insert_db_table(df,tabel_name,curr_name)
            else:
                print(">>",curr_name,"카테고리에",tabel_name,"업데이트중...")
                lastDate = getLastDate(curr_name,tabel_name)
                lastDate = lastDate.replace("-","")

                if lastDate == today:
                    continue

                df = stock.get_market_cap(lastDate, today, str(curr_sym[i]))
                Insert_db_table(df,tabel_name,curr_name)

FinanceData()