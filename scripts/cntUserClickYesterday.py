#!/usr/bin/env python
#encoding=utf8

###################################################################
# Date: 2014/3/31                                                 #
# Count the ratio of user click yesterday and buy today           #
###################################################################

import csv, json
from collections import defaultdict

if __name__ == "__main__":
    paths = json.loads(open("../SETTINGS.json").read())
    data = [entry for entry in csv.reader(open(paths["TAR_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]

    user_behavior = defaultdict(dict)
    for entry in data:
        uid, pid, action_type, month, day = entry
        if month*100+day not in user_behavior[uid]:
            user_behavior[uid][month*100+day] = [set(), set()]
        if action_type == 1:
            user_behavior[uid][month*100+day][1].add(pid)
        elif action_type == 2 or action_type == 3:
            user_behavior[uid][month*100+day][0].add(pid)

    total_num = 0
    hit_num = 0
    for uid in user_behavior:
        for time_key in user_behavior[uid]:
            month = time_key/100
            day = time_key%100
            month1 = month
            day1 = day
            if day == 31:
                month1 += 1
            elif day == 30:
                if month % 2==0:
                    month1 += 1
                else:
                    day1 += 1
            else:
                day1 += 1
            new_time_key = month1*100+day1
            for pid in user_behavior[uid][time_key][0]:
                if pid in user_behavior[uid][time_key][1]:
                    continue
                total_num += 1
                if new_time_key in user_behavior[uid]:
                    if pid in user_behavior[uid][new_time_key][1]:
                        hit_num += 1

    print "Total Num: %d, Hit Num: %d, Ratio: %f" % (total_num, hit_num, 1.0*hit_num/total_num)
