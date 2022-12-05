import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import pickle
from hmmlearn import hmm

SAMPLE_RATE = 20
#filename = "F_23112025-01-2013-05-21-06-21-54.mat.txt"
#filename2 = "F_04835861-01-2013-10-16-13-19-35.mat.txt"
#col = ["relative_time", "absolute_time", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "fall_indicator"]
SIZE = 3
ACT = ["idle", "walk", "stand_up", "sit_down", "fall_forward", "fall_aside"]
for act in ACT:
    col = ["x", "y", "z"]
    df = [[] for i in range(SIZE)]
    acc_set = [[] for i in range(SIZE)]
    av = [[] for i in range(SIZE)]
    vh = [[] for i in range(SIZE)]

    dataslice = np.empty((0, 2))
    length = []
    for i in range(SIZE):
        df[i] = pd.read_csv("./data/" + act + "/" + act + "_" + str(i + 1) + ".txt",\
        header=0, names=col)
        acc_set[i] = df[i][col].to_numpy()
        av[i] = np.average(acc_set[i][0:SAMPLE_RATE-1], axis=0)
        print(av[i])

        for at in acc_set[i]:
            v = np.dot(av[i], at) / np.dot(av[i], av[i])
            avt = v * av[i] 
            aht = at - avt
            h = np.sqrt(np.dot(aht, aht))
            print(v, h)
            vh[i].append([v, h])
        id = 2 * SAMPLE_RATE
        while id < len(vh[i]):
            print(dataslice)
            print(vh[i][id-SAMPLE_RATE:id])
            #dataslice.append(vh[i][id-SAMPLE_RATE:id])
            dataslice = np.concatenate([dataslice, vh[i][id-SAMPLE_RATE:id]])
            length.append(SAMPLE_RATE)
            id += 5
    remodel = hmm.GaussianHMM(n_components=4, covariance_type="diag", n_iter=100)
    remodel.fit(dataslice, length)
    with open(act + ".pkl", "wb") as file: pickle.dump(remodel, file)
    for i in range(len(vh[0]) - SAMPLE_RATE):
        Z = remodel.score(vh[0][i:i+SAMPLE_RATE])
        print(Z)

