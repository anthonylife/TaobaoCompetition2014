#!/usr/bin/env python
#encoding=utf8

import csv, json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

if __name__ == "__main__":
    print("Loading paths...")
    paths = json.loads(open("../SETTINGS.json").read())

    train_data = [data for data in csv.reader(open(paths["TRAIN_DATA_FILE"]))]
    user_history_bought = defaultdict(set)
    for entry in train_data[1:]:
        action_type = int(entry[2])
        if action_type == 0:
            user_history_bought[entry[0]].add(entry[1])

    test_data = [data for data in csv.reader(open(paths["TEST_DATA_FILE"]))]
    user_new_bought = {}
    user_repeated_bought = {}
    for item in test_data[1:]:
        action_type = int(item[2])
        if action_type == 0:
            if item[0] not in user_repeated_bought:
                user_repeated_bought[item[0]] = 0
                user_new_bought[item[0]] = 0
            user_new_bought[item[0]] += 1
            if item[1] in user_history_bought[item[0]]:
                user_repeated_bought[item[0]] += 1

    user_repeated_ratio = {}
    for userid in user_repeated_bought.keys():
        user_repeated_ratio[userid] = float(user_repeated_bought[userid]) / user_new_bought[userid]
    user_repeated_ratio = user_repeated_ratio.items()
    user_repeated_ratio = sorted(user_repeated_ratio, key = lambda x:x[1], reverse=True)
    wfd = open("repeated_ratio.txt", "w")
    for item in user_repeated_ratio:
        wfd.write("%s %f %d\n" % (item[0], item[1], user_new_bought[item[0]]))
    wfd.close()

    user_repeated_bought = user_repeated_bought.items()
    user_repeated_bought = sorted(user_repeated_bought, key= lambda x:x[1], reverse=True)
    wfd = open("repeated_bought.txt", "w")
    for item in user_repeated_bought:
        wfd.write("%s %d\n" % (item[0], item[1]))
    wfd.close()

    repeated_cnt = [item[1] for item in user_repeated_bought]
    userid = [item[0] for item in user_repeated_bought]
    x = np.arange(len(repeated_cnt))
    plt.bar(x, repeated_cnt)
    plt.show()

