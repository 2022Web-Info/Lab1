import torch
import torch.nn as nn

class MF(nn.Module):

    def __init__(self, user_num, item_num, mean , embedding_size, dropout):
        super(MF, self).__init__()
        self.user_emb = nn.Embedding(user_num, embedding_size)
        self.item_emb = nn.Embedding(item_num, embedding_size)
        self.user_bias = nn.Embedding(user_num, 1)
        self.item_bias = nn.Embedding(item_num, 1)

        self.user_emb.weight.data.uniform_(0, 0.005)
        self.item_emb.weight.data.uniform_(0, 0.005)
        self.user_bias.weight.data.uniform_(-0.01, 0.01)
        self.item_bias.weight.data.uniform_(-0.01, 0.01)

        self.mean = nn.Parameter(torch.FloatTensor([mean]), False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, u_id, i_id):
        U = self.user_emb(u_id)
        I = self.item_emb(i_id)
        b_u = self.user_bias(u_id).squeeze()
        b_i = self.item_bias(i_id).squeeze()
        return self.dropout((U * I).sum(1) + b_u + b_i + self.mean)
        