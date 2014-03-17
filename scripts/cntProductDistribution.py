#!/usr/bin/env python
#encoding=utf8

import csv, json
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    print("Loading paths...")
    paths = json.loads(open("../SETTINGS.json").read())

    train_data = [data for data in csv.reader(open(paths["TRAIN_DATA_FILE"]))]
    tr_brandid_set = set([items[1] for items in train_data[1:]])

    test_data = [data for data in csv.reader(open(paths["TEST_DATA_FILE"]))]
    tst_brandid_map = {}
    for item in test_data:
        if item[1] in tr_brandid_set:
            if item[1] in tst_brandid_map:
                tst_brandid_map[item[1]] += 1
            else:
                tst_brandid_map[item[1]] = 1

    tst_brandids = tst_brandid_map.items()
    tst_brandids = sorted(tst_brandids, key= lambda x:x[1], reverse=True)
    #wfd = open("temp_cnt.txt", "w")
    #for item in tst_brandids:
    #    wfd.write("%s %d\n" % (item[0], item[1]))
    #wfd.close()

    brand_count = [item[1] for item in tst_brandids]
    brand_id = [item[0] for item in tst_brandids]
    x = np.arange(len(brand_count))
    plt.bar(x, sorted(brand_count, reverse=True))
    plt.show()


