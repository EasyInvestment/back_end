import pandas as pd
import datetime as datetime
import math
import matplotlib.pyplot as plt
from tqdm import tqdm

class DataLabeling:
    POSITIVE = math.inf
    NEGATIVE = -math.inf
    def __init__(self,data, lookahead_range, target_price,term = 10,alpha = 0.002):
        self.lookahead_range = lookahead_range
        self.data = data   
        self.target_price = target_price
        self.term = term
        self.alpha = alpha

    # lookahead_range 범위안에 더 큰 값이 있는지 확인하는 함수
    def find_max(self,idx):
        for i in range(idx+1,idx + self.lookahead_range + 1):
            if self.data.iloc[i][self.target_price] > self.data.iloc[idx][self.target_price]:
                return False
        return True

    # lookahead_range 범위안에 더 작은 값이 있는지 확인하는 함수
    def find_min(self,idx):
        for i in range(idx+1,idx + self.lookahead_range + 1):
            if self.data.iloc[i][self.target_price] < self.data.iloc[idx][self.target_price]:
                return False
        return True
    def ck(self,idx,term,len_data):
        if idx - term >= 0 and idx + term + 1 < len_data:
            return term
        elif idx - term < 0:
            return idx
        elif idx + term + 1 > len_data:
            return 0
        
    def low_high_vicinity(self,low_label, high_label):
        temp = [2 for i in range(len(self.data))]
        self.data.loc[:, 'label'] = temp
        
        for i in range(len(low_label)):
            idx = low_label[i][0]
            self.data.loc[idx,"label"] = 1
            temp_term = self.ck(idx,self.term,len(self.data))
            low_price = self.data.iloc[idx]["close"]
            
            for j in range(idx-temp_term, idx + temp_term + 1):
                try:
                    if self.data.iloc[j]["close"] < low_price + low_price * self.alpha:
                        self.data["label"][j] = 1
                except IndexError:
                    print("Index out of bounds:",j,idx)


        for i in range(len(high_label)):
            idx = high_label[i][0]
            self.data.loc[idx,"label"] = 0

            temp_term = self.ck(idx,self.term,len(self.data))
            high_price = self.data.iloc[idx]["close"]
            
            for j in range(idx-temp_term, idx + temp_term + 1):
                if self.data.iloc[j]["close"] > high_price - high_price * self.alpha:
                    self.data["label"][j] = 0
    def draw_label(self):
        df = self.data
        fig = plt.figure(figsize=(25,13))
        fig = plt.plot(df.close,color='g')
        line = []
        # ma = self.data[self.target_price].rolling(window=self.ma_window).mean()
        # for i in range(0,self.ma_window):
        #     ma[i] = self.data[self.target_price][i]
        temp = []
        for i in range(len(df)):
            line2 = []
            if df.label[i] == 1:
                fig = plt.scatter(df.index[i],df.iloc[i]['close'],color='r')
                # fig = plt.annotate(df.index[i], xy = (df.index[i+1], df.iloc[i]['close']-1000))
                line2.append(df.index[i])
                line2.append(df.iloc[i]['close'])
                # line2.append(ma[i])
                line2.append(i)
                line.append(line2)
                temp.append(0)
            elif df.label[i] == -1:
                fig = plt.scatter(df.index[i],df.iloc[i]['close'],color='b')
                # fig = plt.annotate(df.index[i], xy = (df.index[i+1], df.iloc[i]['close']-1000))
                line2.append(df.index[i])
                line2.append(df.iloc[i]['close'])
                # line2.append(ma[i])
                line2.append(i)
                line.append(line2)
                temp.append(1)
            else:
                temp.append(2)
        # fig = plt.plot(ma)
        # 상승 : red
        # 하락 : blue
        # 횡보 : gray

        for i in range(0,len(line)-1,1):
            # 상승 구간
            if line[i][1] < line[i + 1][1]:
                fig = plt.plot([line[i][0],line[i+1][0]], [line[i][1],line[i+1][1]],color='red',alpha = 0.5)
                pass
            # 하락 구간
            elif line[i][1] > line[i + 1][1]:
                fig = plt.plot([line[i][0],line[i+1][0]], [line[i][1],line[i+1][1]],color='blue', alpha = 0.5)
                pass
        self.data['label'] = temp
        self.data = self.data.iloc[line[0][3]:line[-1][3]]
        fig = plt.savefig("Labeling_" + str(self.code_name).replace('/','_') +".png")
    def trend(self,high_range,low_range):
        temp = [0 for i in range(len(self.data))]
        self.data['label'] = temp
        
        # fig = plt.figure(figsize=(25,14))
        # fig = plt.plot(self.data.close,color = 'black')
        # 상승구간 0, 하락구간 1
        # 저점 먼저 시작
        if high_range[0][0] > low_range[0][0]:
            for i in tqdm(range(len(high_range))):
                for j in range(2):
                    if i == len(high_range)-1 and j == 1:
                        break
                    if j == 0:
                        idx = [self.data.index[k] for k in range(low_range[i+j][0],high_range[i][0] + 1)]
                        self.data.loc[idx,['label']] = 0
                    else:
                        idx = [self.data.index[k] for k in range(high_range[i][0], low_range[i+j][0] + 1)]
                        self.data.loc[idx,['label']] = 1
        # 고점 먼저 시작
        else:
            for i in tqdm(range(len(low_range))):
                for j in range(2):
                    if i == len(low_range)-1 and j == 1:
                        break
                    if j == 0:
                        idx = [self.data.index[k] for k in range(high_range[i+j][0],low_range[i][0] + 1)]
                        self.data.loc[idx,['label']] = 1
                    else:
                        idx = [self.data.index[k] for k in range(low_range[i][0], high_range[i+j][0] + 1)]
                        self.data.loc[idx,['label']] = 0
    def StartSearching(self):

        # lookahead_range 범위안에서 가장 작은 값과 큰 값의 인덱스 값
        max_index = self.data[self.data[self.target_price] == max(self.data[self.target_price][:self.lookahead_range])].index[0]
        min_index = self.data[self.data[self.target_price] == min(self.data[self.target_price][:self.lookahead_range])].index[0]

        # 숫자로 된 인덱스를 구함
        max_num = [i for i in range(len(self.data)) if max_index == self.data.index[i]][0]
        min_num = [i for i in range(len(self.data)) if min_index == self.data.index[i]][0]
        
        # 만약 고점이 더 늦게 나왔다면 현재 고점부터 먼저 시작 알고리즘 
        if max_index > min_index:
            ck,start = 1,max_num

            # 하지만 lookahead_range 범위 앞에 더 큰 값이 있으면 저점 부터 시작 알고리즘
            if not self.find_max(max_num):
                ck,start = 0,min_num

        elif min_index > max_index:
            ck,start = 0,min_num

            if not self.find_min(min_num):
                ck,start = 1,max_num

        return ck,start
    def find_max(self,idx):
        for i in range(idx+1,idx + self.lookahead_range + 1):
            if self.data.iloc[i][self.target_price] > self.data.iloc[idx][self.target_price]:
                return False
        return True
    def find_min(self,idx):
        for i in range(idx+1,idx + self.lookahead_range + 1):
            if self.data.iloc[i][self.target_price] < self.data.iloc[idx][self.target_price]:
                return False
        return True
    def run(self):
        # ck : 고점 or 저점 시작 여부(0, 1), start_num : 고점 or 저점 시작 인덱스(int)
        ck, start_num = self.StartSearching()

        high_label = [] # 고점들의 리스트
        low_label = [] # 저점들의 리스트
        line = [] # 각 리스트 2차원 리스트

        
        if ck == 0: # 고점을 찾는다
            line.append(start_num)
            line.append(self.data.index[start_num])
            low_label.append(line)

            previous_min = self.data.iloc[start_num][self.target_price]
            max = self.data.iloc[start_num][self.target_price]
            min = self.POSITIVE
        else:
            line.append(start_num)
            line.append(self.data.index[start_num])
            high_label.append(line)
            
            previous_max = self.data.iloc[start_num][self.target_price]
            min = self.data.iloc[start_num][self.target_price]
            max = self.NEGATIVE

            curr_index = 0

        for i in tqdm(range(start_num, len(self.data) - self.lookahead_range)):
            line = []
            if ck == 0:
                if self.data.iloc[i][self.target_price] > max and self.data.iloc[i][self.target_price] >= previous_min: # 만약 현재 인덱스 값이 max보다 클시
                    if self.data.iloc[i + 1:i + self.lookahead_range + 1][self.target_price].max() < self.data.iloc[i][self.target_price]: # 만약에 앞에 term일 동안 더 큰 값이 없으면 고점이라고 판단
                        line.append(i)
                        line.append(self.data.index[i])
                        high_label.append(line)

                        previous_max = self.data.iloc[i][self.target_price]
                        max = self.NEGATIVE
                        ck = 1

                        curr_index = i
                    elif not self.find_max(i): # 만약 앞에 term일 동안 더 큰 값이 있으면 고점이 아님 , max값만 업데이트
                        max = self.data.iloc[i][self.target_price]
            elif ck == 1: # 저점을 찾는다.
                if self.data.iloc[i][self.target_price] < min and self.data.iloc[i][self.target_price] <= previous_max:
                    if self.data.iloc[i+1:i+self.lookahead_range+1][self.target_price].min() > self.data.iloc[i][self.target_price]:
                        line.append(i)
                        line.append(self.data.index[i])
                        low_label.append(line)
                        
                        previous_min = self.data.iloc[i][self.target_price]
                        min = self.POSITIVE
                        ck = 0

                        curr_index = i
                    elif not self.find_min(i):
                        min = self.data.iloc[i][self.target_price]
        # curr_index : 마지막 라벨 인덱스
        last_index = -1

        # 라벨 체크를 다하고 남은 데이터에 대한 처리
        for i in tqdm(range(curr_index,len(self.data))):
            
            if self.data.iloc[i][self.target_price] == max:
                last_index = i
            
            elif self.data.iloc[i][self.target_price] == min:
                last_index = i
            
            elif self.data.iloc[i][self.target_price] > max and ck == 0:
                last_index = i
                max = self.data.iloc[i][self.target_price]
            
            elif self.data.iloc[i][self.target_price] < min and ck == 1:
                last_index = i
                min = self.data.iloc[i][self.target_price]
            
        if ck == 0:
            line.append(last_index)
            line.append(self.data.index[last_index])
            high_label.append(line)
        else:
            line.append(last_index)
            line.append(self.data.index[last_index])
            low_label.append(line)
        self.trend(low_label,high_label)
        return low_label, high_label