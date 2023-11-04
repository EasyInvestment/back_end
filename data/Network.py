import pandas as pd
import numpy as np
import keras
from keras.models import Model
from keras.layers import Input, Dense, LSTM, Conv1D, \
    BatchNormalization, Dropout, MaxPooling1D, Flatten
import tensorflow as tf
from tqdm import tqdm
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
# from Indicator import *
# from DataScaler import *

class Network:
    def __init__(self,input_dim = 0, output_dim = 0, lr = 0.001,
                activation = "relu", loss = "BC"):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.lr = lr
        self.activation = activation
        if loss == "mse":
            self.loss = tf.keras.losses.MeanSquaredError()
        elif loss == "BC":
            self.loss = tf.keras.losses.BinaryCrossentropy()
    
    def predict(self,x):
        pass

class DNN(Network):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = self.get_network_head()
        self.model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.lr),
                           metrics=[tf.keras.metrics.BinaryAccuracy()],
                            loss = self.loss)

    def get_network_head(self):
        model = keras.models.Sequential()
        model.add(keras.layers.Dense(256,input_shape = (self.input_dim,)))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(128,activation=self.activation))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(64,activation=self.activation))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(32,activation=self.activation))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(1,activation="sigmoid"))
        return model

    def train_on_batch(self, x, y):
        self.model.fit(x,y,batch_size = 1024, epochs = 100)

    def predict(self, sample):
        sample = np.array(sample).reshape((-1, self.input_dim))
        return self.model.predict(sample)
    
class LSTMNetwork(Network):
    def __init__(self, num_steps, input_dim, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_steps = num_steps
        self.input_dim = input_dim
        self.model = self.get_network_head()
        self.model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.lr),
                           metrics=[tf.keras.metrics.BinaryAccuracy()],
                            loss=self.loss)
    def make_dataset(self,data, label, window_size=20):
        feature_list = []
        label_list = []
        print(">>LSTM Data transpose")
        for i in tqdm(range(len(data) - window_size)):
            feature_list.append(np.array(data.iloc[i:i+window_size]))
            label_list.append(np.array(label.iloc[i+window_size - 1]))
        return np.array(feature_list), np.array(label_list)
    def get_network_head(self):
        model = keras.models.Sequential()
        model.add(LSTM(256, input_shape = (self.num_steps,self.input_dim)))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(128,activation=self.activation))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(64,activation=self.activation))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(32,activation=self.activation))
        model.add(keras.layers.Dropout(0.1))
        model.add(keras.layers.Dense(1,activation="sigmoid"))
        return model

    def train_on_batch(self, x, y):
        x,y = self.make_dataset(x,y)
        self.model.fit(x, y, batch_size = 1024, epochs = 100)

    def predict(self, x):
        pred = self.model.predict(x)
        return pred
class LogisticNetwork(Network):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = self.get_network_head()
        self.model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=[tf.keras.metrics.BinaryAccuracy()])
    def get_network_head(self):
        model = keras.models.Sequential()
        model.add(keras.layers.Dense(256,input_shape = (self.input_dim,)))
        model.add(keras.layers.Dense(1))
        return model

    def train_on_batch(self,x,y):
        self.model.fit(x,y,batch_size = 256, epochs = 100)
        
class Xgboost(Network):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = self.get_network_head()

    def get_network_head(self):
        return XGBClassifier(max_depth = 5)
    
    def train_on_batch(self,x,y):
        self.model.fit(x, y)
        

class ensembleModel:
    def __init__(self,num_step, input_dim):
        self.num_step = num_step
        self.DNNModel = DNN(input_dim = input_dim)
        self.LSTMModel = LSTMNetwork(input_dim = input_dim, num_steps = num_step)
        self.LRModel = LogisticNetwork(input_dim = input_dim)
        self.XGBoostModel = Xgboost(input_dim = input_dim)
    def models_fit(self,x,y):
        print(">> DNN Training...")
        self.DNNModel.train_on_batch(x,y)
        print(">> Logistic Training...")
        self.LRModel.train_on_batch(x,y)
        print(">> XGBoost Training...")
        self.XGBoostModel.train_on_batch(x,y)
        print(">> LSTM Training...")
        self.LSTMModel.train_on_batch(x,y)
    #  0 <= threshold < 0.5
    def predict_and_evaluation(self,x_test,y_test, threshold = 0.2):

        self.DNNPredict = self.DNNModel.predict(x_test)
        self.LRPredict = self.LRModel.model.predict(x_test)
        self.XGBoostPredict = self.XGBoostModel.model.predict(x_test)
        LSTM_x_test, LSTM_y_test = self.LSTMModel.make_dataset(x_test,y_test)
        self.LSTMPredict = self.LSTMModel.predict(LSTM_x_test)

        self.DNNPredict = self.DNNPredict.reshape(-1,)
        self.LRPredict = self.LRPredict.reshape(-1,)
        self.XGBoostPredict = self.XGBoostPredict.reshape(-1,)
        self.LSTMPredict = list([-1 for i in range(self.num_step)]) + list(self.LSTMPredict.reshape(-1,))

        self.result_label = []
        cnt = 0
        for i in range(len(self.DNNPredict)):
            if self.DNNPredict[i] > 1 - threshold:
                self.result_label.append(1)
            elif self.DNNPredict[i] < threshold:
                self.result_label.append(0)
            else:
                self.result_label.append(-1)
                cnt += 1

        ck = 0 # 정답 카운트
        cnt = 0 # 총 카운트
        for i in range(len(self.result_label)):
            if self.result_label[i] != -1:
                if self.result_label[i] == y_test.iloc[i]:
                    ck += 1
                cnt += 1
        if ck == 0:
            return 0
        else:
            return round(ck/cnt * 100,2)