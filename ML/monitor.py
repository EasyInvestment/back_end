# from StockDataLoad import FinanceData
from .GetData import dataAll
from Network import ensembleModel
from dataIndicator import *
from sklearn.preprocessing import StandardScaler

def make_dataset(data, label, window_size=20):
    feature_list = []
    label_list = []
    for i in range(len(data) - window_size):
        feature_list.append(np.array(data[i:i+window_size]))
        label_list.append(np.array(label.iloc[i+window_size - 1]))
    return np.array(feature_list), np.array(label_list)

def monitor(category =None,stockName = None,LabelingValue = 120,seq_len = 20,offset = True):
    # return pd.read_csv("labeled_data_BTC_USDT_1h_70.csv",index_col=0)
    # 데이터 업데이트
    # FinanceData()

    # 데이터 불러오기
    stockData = dataAll(category,stockName)
    stockData = stockData.drop(["timestamp"],axis=1)
    stockData.columns = [curr_name.lower() for curr_name in stockData.columns]

    # 데이터 라벨링
    from DataLabeling import DataLabeling
    labeling = DataLabeling(stockData, LabelingValue, "close")
    labeling.run()
    data = labeling.data

    # 보조지표 추가
    data = add_rsi(data)
    data = add_ma(data,period=7)
    data = add_ema(data,period=7)
    data = add_ma(data,period=25)
    data = add_ema(data,period=25)
    data = add_ma(data,period=99)
    data = add_ema(data,period=99)
    data = add_stochastic(data)
    data = add_bb(data,length=21)
    data = add_disparity(data,period=25)
    data = add_macd(data)
    data = add_kdj(data)
    data = data.dropna()


    X,Y = data.drop(['label'],axis = 1),data['label']
    X = StandardScaler().fit_transform(X)
    # 데이터 분리
    if offset == True:
        test_size = int(len(data) * 0.2)
        x_train = X[:test_size]
        y_train = Y[:test_size]
        x_test = X[test_size:]
        y_test = Y[test_size:]
    else:
        x_train,y_train = X,Y
    
    # 모델 학습
    model = ensembleModel(seq_len,x_train.shape[1])
    model.models_fit(x_train,y_train)

    if offset == True:
        from sklearn.metrics import classification_report
        pred = model.predict_and_evaluation(x_test,y_test)
        result = []
        for i in range(len(model.LSTMPredict)):
            curr_pred = model.LSTMPredict[i]
            if curr_pred < 0.5:
                result.append(0)
            else:
                result.append(1)
        print(classification_report(result,y_test.tolist()))
        x_test,_ = make_dataset(x_test,y_test)
        return model.LSTMModel.predict(x_test)
    else:
        model.predict(offset)
