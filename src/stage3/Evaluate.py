import torch
import numpy as np
import math

def loss_function(predict, score):
    return torch.sum((predict-score)**2)


def metrics(model, evaluate_set:dict):
    """
        evaluate_set 是一个列表,每个元素是一个字典,存了 电影ID->评分
    """
    NDCG = 0
    count = 0
    for user_id, item_dic in enumerate(evaluate_set):
        item_id = list(item_dic.keys())
        user = torch.full((len(item_id),),user_id,dtype=torch.int64).cuda()
        item = torch.tensor(item_id,dtype=torch.int64).cuda()
        prediction = model(user, item).detach().cpu().numpy()[:,np.newaxis]
        temp = np.array(list(item_dic.values()))[:,np.newaxis]
        # rank 是一个列表 [[predict,score],...] 按照 predict 的分数降序
        rank = np.concatenate([prediction,temp],axis=1).tolist()
        rank.sort(reverse=True)
        DCG = 0
        for i,(_,score) in enumerate(rank):
            DCG += (2**score - 1) / math.log2(i+2)  # 因为 i 从 0 开始所以额外加1
        iDCG = 0
        iRank = list(item_dic.values())
        iRank.sort(reverse=True)
        for i, score in enumerate(iRank):
            iDCG += (2**score - 1) / math.log2(i+2)
        if iDCG != 0:
            NDCG_i = DCG / iDCG
            NDCG += NDCG_i
            count += 1
    return NDCG / count
