import torch
import Model
import pandas as pd
import numpy as np
from Dataset import readData

model = torch.load("./Model/MF_DoubanMovie_0.005lr_0dropout_20factornum.pth")
_, _, test_dic, _ = readData("./New_Movie_score.csv")

test_set = []
for i, item_dict in enumerate(test_dic):
    user_dic = dict()
    user_dic['user_id'] = i
    user_dic['rank_gt'] = []
    user_dic['rank_predict'] = []

    item_id = list(item_dict.keys())
    user = torch.full((len(item_id), ), i, dtype=torch.int64).cuda()
    item = torch.tensor(item_id, dtype=torch.int64).cuda()
    prediction = model(user, item).detach().cpu().numpy()[:, np.newaxis]

    # 记录正确的排序
    item_id = np.array(item_id)[:, np.newaxis]
    item_score = np.array(list(item_dict.values()))[:, np.newaxis]
    rank_gt = np.concatenate([item_score, item_id], axis=1).tolist()
    rank_gt.sort(reverse=True)
    for sc, id in rank_gt:
        user_dic['rank_gt'].append(f"{id}({sc})")

    # 记录预测的排序
    rank_predict = np.concatenate([prediction, item_id, item_score], axis=1).tolist()
    rank_predict.sort(reverse=True)
    for predic, id, sc in rank_predict:
        user_dic['rank_predict'].append(f"{int(id)}({int(sc)})")
    test_set.append(user_dic)

col_name = ['user_id', 'rank_predict', 'rank_gt']
pd.DataFrame(test_set, columns=col_name).to_csv("./rank_result.csv", index=False)
