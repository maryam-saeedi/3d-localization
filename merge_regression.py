from sklearn.linear_model import LinearRegression
import numpy as np

def merge(set1, set2):
    set1 = np.reshape(set1, (17, 3))
    set2 = np.reshape(set2, (17, 3))

    common1 = []
    common2 = []
    unique1 = []
    unique2 = []
    for idx, (k1, k2) in enumerate(zip(set1, set2)):
        if k1[0] == -1.0 and k2[0] == -1.0:
            continue
        if k2[0] == -1.0:
            unique1.append((idx,k1))
        elif k1[0] == -1.0:
            unique2.append((idx,k2))
        else:
            common1.append(k1)
            common2.append(k2)

    if len(unique1) > 0:
        model = LinearRegression()
        model.fit(common1, common2)
        predicted_key1 = model.predict([x[1] for x in unique1])
        for i, u1 in enumerate(unique1):
            set2[u1[0]] = predicted_key1[i]
    if len(unique2)>0:
        model2 = LinearRegression()
        model2.fit(common2, common1)
        predicted_key2 = model2.predict([x[1] for x in unique2])
        for i, u2 in enumerate(unique2):
            set1[u2[0]] = predicted_key2[i]

    return set1, set2
