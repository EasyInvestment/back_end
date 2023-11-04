import pandas as pd
import numpy as np
import os
def FindIndices():
    l = os.listdir("resultData")
    df_list = []
    for i in range(len(l)):
        df_list.append(pd.read_csv("resultData/"+l[i],index_col=0))
    minDate = min([df_list[i].index[0] for i in range(len(df_list))])
    maxDate = max([df_list[i].index[-1] for i in range(len(df_list))])

    date_range = pd.date_range(minDate, maxDate)
    resultdf = pd.DataFrame({'날짜': date_range})


    Industry_Price_Index = []
    for i in range(len(resultdf)):
        curr_date = str(resultdf.iloc[i]["날짜"])[:10]
        
        for j in range(len(df_list)):
            total_curr_price_c = 0
            total_curr_price_o = 0
            total_curr_price_h = 0
            total_curr_price_l = 0
            cnt = 0
            total_curr_market = 0
            try:
                curr_price_c = df_list[j].loc[curr_date]["Close"]
                curr_market = df_list[j].loc[curr_date]["Close"]

                curr_price_o = df_list[j].loc[curr_date]["Open"]
                curr_price_h = df_list[j].loc[curr_date]["High"]
                curr_price_l = df_list[j].loc[curr_date]["Low"]

            except:
                continue
            if curr_market == np.NaN:
                curr_market = np.mean(df_list[j]["시가총액"].dropna().tolist())
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