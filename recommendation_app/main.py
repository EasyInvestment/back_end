from monitor import monitor
import pandas as pd
from GetData import getTableName
def main():
    # offset에 데이터주면 예측값 반환
    cate = pd.read_csv("cate.csv",index_col=0).iloc[:10]
    result = []
    name = []
    for i in range(len(cate)):
        try:
            curr = cate.iloc[i]["name"]
            curr_table = getTableName(curr)[-1]
            re = monitor(curr,curr_table,LabelingValue=20,offset = True)
            # if re[-1][0] > 0.5:
            #     print("상승 추세")
            # else:
            #     print("하락 추세")
            result.append(re[-1][0])
            name.append(curr)
        except:
            pass
    df = pd.DataFrame(result,columns = ["pred"])
    df["name"] = name
    df = df.sort_values(["pred"])
    return (df["name"].iloc[-4:].to_numpy().tolist())
    # return df.iloc[-4:].to_numpy().tolist()