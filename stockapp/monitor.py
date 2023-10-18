import pandas as pd

def monitor(category =None,stockName = None,LabelingValue = 120,seq_len = 20,offset = True):
    return pd.read_csv("static/labeled_data_BTC_USDT_1h_70.csv",index_col=0)