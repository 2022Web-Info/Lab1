import torch
import numpy as np
import pandas as pd

data = pd.read_csv("./New_Movie_score.csv")
scores = np.array(list(data.loc[:,'movie_score']))
print(np.mean(scores))