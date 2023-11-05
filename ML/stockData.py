import FinanceDataReader as fdr
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import FinanceDataReader as fdr
import os
import chromedriver_autoinstall
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

def stockData():
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
    os.makedirs("stockData")
    
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
        os.makedirs("stockData/"+curr_name)
        for i in range(len(curr_sym)):
            df = fdr.DataReader(curr_sym[i])
            df.to_csv("stockData/"+curr_name+"/"+curr_sym[i]+".csv")
# stockData()