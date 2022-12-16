import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import pickle
from hmmlearn import hmm

SAMPLE_RATE = 20
LAST = 8
#filename = "F_23112025-01-2013-05-21-06-21-54.mat.txt"
#filename2 = "F_04835861-01-2013-10-16-13-19-35.mat.txt"
#col = ["relative_time", "absolute_time", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "fall_indicator"]
SIZE = 6
ACT = ["idle", "walk", "stand_up", "sit_down", "fall_forward"]
#state = {"sit_down" : "sit", "fall_forward" : "lay", "fall_aside" : "lay2", "stand_up" : "idle2"}
size = {"idle" : 5, "walk" : 5, "stand_up" : 5, "sit_down" : 5, "fall_forward" : 3}
for act in ACT:
    print(act)
    col = ["x", "y", "z"]
    df = [[] for i in range(size[act])]
    acc_set = [[] for i in range(size[act])]
    av = [[] for i in range(size[act])]
    vh = [[] for i in range(size[act])]

    dataslice = []
    dataslice2 = np.empty((0, 2))
    length = []
    length2= []
    for i in range(size[act]):
        print(act, i)
        df[i] = pd.read_csv("./data/" + act + "/" + act + "_" + str(i + 1) + ".txt",\
        header=0, names=col)
        acc_set[i] = df[i][col].to_numpy()
        av[i] = np.average(acc_set[i][0:SAMPLE_RATE-1], axis=0)
        #print(av[i])
        lav = np.sqrt(np.dot(av[i], av[i]))
        for at in acc_set[i]:
            v = float(np.dot(av[i], at) / lav) 
            avt = (v / lav) * av[i] 
            aht = at - avt
            h = float(np.sqrt(np.dot(aht, aht)))
            #print(v, h)
            vh[i].append([v, h])
        id = LAST 
        while id < len(vh[i]):
            #dataslice = np.concatenate([dataslice, vh[i][id-LAST:id]])
            # dataslice.append(np.array(vh[i][id-LAST:id]))
            #dataslice = dataslice + vh[i][id-LAST:id]
            for j in range(LAST):
                dataslice.append(vh[i][j+id-LAST])
            length.append(LAST)
            id += LAST 
    dataslice = np.array(dataslice)
    print(dataslice)
    remodel = hmm.GaussianHMM(n_components=4, n_iter=100)
    remodel.fit(dataslice, length)
    with open(act + ".pkl", "wb") as file: pickle.dump(remodel, file)
        #print(Z)
    df = pd.DataFrame(vh[0], columns = ["v", "h"]) 
    df.to_csv("_" + act + "_vh.txt")

