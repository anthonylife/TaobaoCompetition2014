#!/usr/bin/env python
#encoding=utf8

###################################################################
# Date: 2014/3/31                                                #
# Output format: uid, (1)bought num, (2)click num                 #
###################################################################
import csv, json


if __name__ == "__main__":
    paths = json.loads(open("../SETTINGS.json").read())
    data = [entry for entry in csv.reader(open(paths["TRAIN_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]

    user_behavior = {}
    for entry in data:
        uid, pid, action_type = entry[:3]
        if uid not in user_behavior:
            user_behavior[uid] = [set(), set()]
        if action_type == 1:
            user_behavior[uid][0].add(pid)
        elif action_type == 0:
            user_behavior[uid][1].add(pid)

    user_sorted = sorted(user_behavior.items(), key=lambda x:len(x[1][0])+len(x[1][1]))

    wfd = open("user_behavior.txt", "w")
    for i in xrange(len(user_sorted)):
        wfd.write("%d\t%d\t%d\n" % (user_sorted[i][0], len(user_sorted[i][1][0]), len(user_sorted[i][1][1])))
    wfd.close()
