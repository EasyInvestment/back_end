import FinanceDataReader as fdr
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import pymysql
import FinanceDataReader as fdr
import os
import chromedriver_autoinstall
from sqlalchemy import create_engine
import sqlalchemy
from pykrx import stock

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
def connect_db(database):
    host = "investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com"
    port = 3306
    username = "someone555"
    database = database
    password = "12345asdfg"
    try:
        con = pymysql.connect(host=host, user=username, password=password,
                db=database, charset='utf8') # 한글처리 (charset = 'utf8')
    except:
        print(">> connection 실패 ")
        return False

    return con
def connect():
    host = "investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com"
    port = 3306
    username = "someone555"
    password = "12345asdfg"
    try:
        con = pymysql.connect(host=host, user=username, password=password, charset='utf8') # 한글처리 (charset = 'utf8')
    except:
        print(">> connection 실패 ")
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
    except Exception as e:
        # 오류 발생 시 롤백
        con.rollback()
        print(f"데이터베이스 생성 중 오류 발생: {e}")
    finally:
        # 연결 닫기
        con.close()
def Create_db_table(name,database_name):
    # STEP 2: MySQL Connection 연결
    print(">> MySql Connection중..")
    try:
        con = connect_db(database_name)
        print(">> Connection complate!")
    except:
        print(">> Connection 실패")
        return False
    # STEP 3: Connection 으로부터 Cursor 생성
    cur = con.cursor()
    if cur == False:
        return
    sql = '''CREATE TABLE '''+ name.replace('/','_')+'''(
            timestamp datetime,
            open float(32),
            high float(32),
            low float(32),
            close float(32),
            volume float(32),
            Change float(32),
            )
    '''
    try:
        cur.execute(sql) # sql문  실행
        print(">> "+name.replace('/','_')+" 테이블 생성 성공!")
    except pymysql.err.OperationalError:
        print(">> 테이블 생성 실패 : 이미 생성된 테이블입니다.")
        return False
    except pymysql.err.ProgrammingError:
        print(">> 테이블 생성 실패 : sql문 에러입니다.")
        return False
    return True

def Insert_db_table(df,name,database_name):
    print(">> MySql Connection중..")
    try:
        db_connection_str = "mysql+pymysql://someone555:12345asdfg@investment.cu24cf6ah5lb.us-west-1.rds.amazonaws.com/"+database_name
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()
        print(">> Connection complate!")
    except:
        print(">> Connection 실패")
        return df
    df['timestamp'] = df.index
    dtypesql = {"timestamp":sqlalchemy.types.DateTime(), 
            'open':sqlalchemy.types.Float(32), 
            'high':sqlalchemy.types.Float(32),
            'low':sqlalchemy.types.Float(32),
            'close':sqlalchemy.types.Float(32),
            'volume':sqlalchemy.types.Float(32),
            'Change':sqlalchemy.types.Float(32),
    }
    print(">> 데이터베이스에 데이터 업로드 시작")
    try:
        df.to_sql(name = name.replace('/','_'),con = conn,if_exists='append',index=False,dtype = dtypesql)
        print(">> 데이터 업로드 성공!")
        return True
    except:
        print(">> 데이터 업로드 실패... 파라미터를 확인하세요")
        return df
    
def FinanceData():
    # 카테고리 수집
    # driver = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())
    driver = chrome_driver()
    driver.get("https://finance.naver.com/sise/sise_group.naver?type=upjong")

    sector = driver.find_elements(By.CSS_SELECTOR,"#contentarea_left > table > tbody > tr > td > a")
    sector_url = [curr.get_attribute("href") for curr in sector]
    sector_name = [curr.text for curr in sector]

    # 주식 카테고리 별 이름 데이터
    category = []
    for i in range(len(sector_url)):
        driver.get(sector_url[i])
        sectorDetail = driver.find_elements(By.CSS_SELECTOR, "#contentarea > div:nth-child(5) > table > tbody > tr > td.name")
        companyName = [curr.text.replace("*","").replace(" ","") for curr in sectorDetail]

        category.append(companyName)

    data = pd.DataFrame(category)
    data["index"] = sector_name
    data = data.set_index("index")
    
    # 한국거래소 상장종목 전체
    df_krx = fdr.StockListing('KRX')
    for k in range(len(data)):
        curr_category = data.iloc[k].dropna().tolist()
        curr_name = data.index[k]
        curr_sym = []
        for i in range(1,len(curr_category)):
            try:
                curr_sym.append(df_krx[df_krx["Name"] == curr_category[i]]["Symbol"].values[0])
            except:
                pass
        CreateDB(curr_name)
        for i in range(len(curr_sym)):
            tabel_name = "s"+curr_sym[i]
            Create_db_table(tabel_name,curr_name)
            df = fdr.DataReader(curr_sym[i])
            Insert_db_table(df,tabel_name,curr_name)
            # df.to_csv("stockData/"+curr_name+"/"+curr_sym[i]+".csv")