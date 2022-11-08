import Model
import Evaluate
import Dataset
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import os

def train(model, optimizer, loss_function, data_loader):
    model.train()
    for user, item, score in tqdm(data_loader, leave=False):
        user = user.cuda()
        item = item.cuda()
        score = score.float().cuda()

        model.zero_grad()
        prediction = model(user,item)
        loss = loss_function(prediction,score)
        loss.backward()
        optimizer.step()
    return None

def run():
    # 一些参数
    lr = 0.005
    dropout = 0
    batch_size = 2048
    epochs = 20
    factor_num = 20
    user_num = 545
    item_num = 1000

    os.environ['CUDA_LAUNCH_BLOCKING'] = '1' # 下面老是报错 shape 不一致
    
    # 准备数据集和模型
    trainData, validSet, testSet, mean = Dataset.readData("./Movie_score.csv")
    trainSet = Dataset.DoubanMovie(trainData)
    train_loader = DataLoader(trainSet, batch_size=batch_size, shuffle=True, num_workers=4)
    model = Model.MF(user_num,item_num,mean,factor_num,dropout)       
    model.cuda()     
    loss_function = Evaluate.loss_function    
    optimizer = torch.optim.Adam(model.parameters(), lr = lr)

    # 训练
    best_model, best_ndcg, best_epoch, result_ndcg = None, 0, 0, 0

    try:
        for epoch in tqdm(range(epochs), leave=False):
            train(model, optimizer, loss_function, train_loader)
            model.eval()
            valid_ndcg = Evaluate.metrics(model,validSet)
            test_ndcg = Evaluate.metrics(model,testSet)
            if valid_ndcg > best_ndcg:
                best_ndcg = valid_ndcg
                best_epoch = epoch
                result_ndcg = test_ndcg
                best_model = model
            tqdm.write(f"epoch_{epoch}: valid_ndcg is {valid_ndcg}, test_ndcg is {test_ndcg}")
                
    finally:
        model_path = "./Model/"
        if not os.path.exists(model_path):
            os.mkdir(model_path)
        torch.save(
            best_model,
            f'./Model/MF_DoubanMovie_{lr}lr_{dropout}dropout_{factor_num}factornum.pth')
        tqdm.write("End train and valid. Best validation epoch is {:03d}, ndcg is {}.".format(
            best_epoch, result_ndcg))
            
if __name__ == "__main__":
    run()
