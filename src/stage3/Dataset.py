from torch.utils.data import Dataset
import pandas as pd
import numpy as np


def readData(data_path):
    print("reading data...")
    user_num = 545
    # 读取评分数据，将数据按时间排序，并按照 8：1：1划分数据集
    data = pd.read_csv("./New_Movie_score.csv")
    data.sort_values(by='time', ascending=True, inplace=True)
    # index 得重排，不然切片会出错
    data = data.loc[:, ['user_id', 'movie_id', 'movie_score']].reset_index()
    size = data.shape[0]
    temp_scores = np.array(list(data.loc[:,'movie_score']))
    mean = np.mean(temp_scores) # 平均分
    # loc 取的是双闭区间
    trainSet = data.loc[:int(0.8 * size)-1].reset_index()
    validSet = data.loc[int(0.8 * size):int(0.9 * size)-1].reset_index()
    testSet = data.loc[int(0.9*size):].reset_index()
    valid_dic = [dict() for _ in range(user_num)]
    for i in range(user_num):
        itemSet = validSet.loc[validSet['user_id']==i]
        for _, it in itemSet.iterrows():
            valid_dic[i][int(it['movie_id'])] = int(it['movie_score'])
    test_dic = [dict() for _ in range(user_num)]
    for i in range(user_num):
        itemSet = testSet.loc[testSet['user_id']==i]
        for _, it in itemSet.iterrows():
            test_dic[i][int(it['movie_id'])] = int(it['movie_score'])
    return trainSet,valid_dic,test_dic, mean

class DoubanMovie(Dataset):

    def __init__(self, data) -> None:
        super().__init__()
        self.data = data

    def __len__(self):
        return self.data.shape[0]
    
    def __getitem__(self, index):
        return self.data.loc[index,'user_id'], self.data.loc[index,'movie_id'], self.data.loc[index,'movie_score']

# debug
if __name__ == "__main__":
    path = "./Movie_score.csv"
    data = pd.read_csv(path)
    train,valid,test = readData(path)
    print(valid)
    trainSet = DoubanMovie(train)
    print(trainSet[0])
