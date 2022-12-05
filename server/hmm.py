import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
from hmmlearn import hmm

SAMPLE_RATE = 20
filename = "F_23112025-01-2013-05-21-06-21-54.mat.txt"
filename2 = "F_04835861-01-2013-10-16-13-19-35.mat.txt"
col = ["relative_time", "absolute_time", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "fall_indicator"]

df = pd.read_csv("csv/" + filename, header=0, names=col)
print(df["fall_indicator"])

l = df.loc[df["fall_indicator"] > 0] 
tmp = df[12000 - 10 : 12000 + 10]

acc_set = df[["ax", "ay", "az"]][0:SAMPLE_RATE-1].to_numpy()
print(np.average(acc_set, axis=0))
av = np.average(acc_set, axis=0)
acc_set = df[["ax", "ay", "az"]][12000 - 10:12000 + 10].to_numpy()
vh = []
for at in acc_set:
    avt = np.dot(av, at) / np.dot(av, av) * av 
    aht = at - avt
    v = np.dot(av, at) / np.sqrt(np.dot(av, av))
    h = np.sqrt(np.dot(aht, aht))
    print(v, h)
    vh.append([v, h])
#print(vh)
remodel = hmm.GaussianHMM(n_components=4, covariance_type="diag", n_iter=100)
remodel.fit(vh)
vh2 = []
acc_set = df[["ax", "ay", "az"]][0:SAMPLE_RATE-1].to_numpy()
for at in acc_set:
    avt = np.dot(av, at) / np.dot(av, av) * av 
    aht = at - avt
    v = np.dot(av, at) / np.sqrt(np.dot(av, av))
    h = np.sqrt(np.dot(aht, aht))
    print(v, h)
    vh2.append([v, h])
remodel2 = hmm.GaussianHMM(n_components=4, covariance_type="diag", n_iter=100)
remodel2.fit(vh2)
Z2 = remodel2.score(vh)
Z = remodel.score(vh)
print(Z)
print(Z2)
tmp.to_csv("fall_extract_csv.txt")
print(df.loc[df["fall_indicator"] > 0])

