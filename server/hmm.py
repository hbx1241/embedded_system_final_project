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
SIZE = 6
ACT = ["idle", "walk", "stand_up", "sit_down", "fall_forward", "fall_aside"]
state = {"sit_down" : "sit", "fall_forward" : "lay", "fall_aside" : "lay2", "stand_up" : "idle2"}
size = {"idle" : 5, "walk" : 6, "stand_up" : 3, "sit_down" : 6, "fall_forward" : 3, "fall_aside" : 3}
for act in ACT:
    col = ["x", "y", "z"]
    df = [[] for i in range(size[act])]
    acc_set = [[] for i in range(size[act])]
    av = [[] for i in range(size[act])]
    vh = [[] for i in range(size[act])]

    dataslice = np.empty((0, 2))
    dataslice2 = np.empty((0, 2))
    length = []
    length2= []
    for i in range(size[act]):
        df[i] = pd.read_csv("./data/" + act + "/" + act + "_" + str(i + 1) + ".txt",\
        header=0, names=col)
        acc_set[i] = df[i][col].to_numpy()
        av[i] = np.average(acc_set[i][0:SAMPLE_RATE-1], axis=0)
        #print(av[i])
        lav = np.sqrt(np.dot(av[i], av[i]))
        for at in acc_set[i]:
            v = np.dot(av[i], at) / lav 
            avt = (v / lav) * av[i] 
            aht = at - avt
            h = np.sqrt(np.dot(aht, aht))
            #print(v, h)
            vh[i].append([v, h])
        if act in state:
            time_df = pd.read_csv("./data/" + act + "/" + act + "_time.txt", header=0) 
            st = time_df["st"][i]
            ed = time_df["end"][i]
            id = st + SAMPLE_RATE
            while id < ed:
                dataslice = np.concatenate([dataslice, vh[i][id-SAMPLE_RATE:id]])
                length.append(SAMPLE_RATE)
                id += SAMPLE_RATE 
            id = ed + SAMPLE_RATE
            while id < len(vh[i]):
                dataslice2 = np.concatenate([dataslice2, vh[i][id-SAMPLE_RATE:id]])
                length2.append(SAMPLE_RATE)
                id += 1 
        else:
            id = 2 * SAMPLE_RATE
            while id < len(vh[i]):
                dataslice = np.concatenate([dataslice, vh[i][id-SAMPLE_RATE:id]])
                length.append(SAMPLE_RATE)
                id += 1 
    remodel = hmm.GaussianHMM(n_components=4, n_iter=100)
    remodel.fit(dataslice, length)
    with open(act + ".pkl", "wb") as file: pickle.dump(remodel, file)
    if act in state:
        print(state[act])
        remodel2 = hmm.GaussianHMM(n_components=4, n_iter=100)
        remodel2.fit(dataslice2, length2)
        with open(state[act] + ".pkl", "wb") as file: pickle.dump(remodel2, file)
    for i in range(len(vh[0]) - SAMPLE_RATE):
        Z = remodel.score(vh[0][i:i+SAMPLE_RATE])
        #print(Z)
    df = pd.DataFrame(vh[0], columns = ["v", "h"]) 
    df.to_csv("_" + act + "_vh.txt")

