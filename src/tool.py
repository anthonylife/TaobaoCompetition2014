#!/usr/bin/env python
#encoding=utf8

#Copyright [2014] [Wei Zhang]

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

###################################################################
# Date: 2014/3/17                                                 #
# contain some useful functions                                   #
###################################################################

import sys, csv, json, datetime, random, math

settings = json.loads(open("/home/anthonylife/Doctor/Code/Competition/taobao2014/SETTINGS.json").read())

def calSegNum(month, day):
    if month == 4:
        return 1
    elif month == 5 and day < 15:
        return 1
    elif month == 5 and day >= 15:
        return 2
    elif month == 6 and day < 15:
        return 2
    elif month == 6 and day >= 15:
        return 3
    elif month == 7 and day < 15:
        return 3
    elif month == 7 and day >= 15:
        return 4
    elif month == 8 and day <= 15:
        return 4
    else:
        print 'date exceed specified range...'
        sys.exit(1)


def calSegNum1(month, day, time_seg_node):
    num_seg = len(time_seg_node) - 1
    for i in range(num_seg):
        if inTimeInterval(month, day, time_seg_node[i], time_seg_node[i+1]):
            return i
    return -1


def inTimeInterval(month, day, interval1, interval2):
    if month > interval1[0]:
        return False
    elif month == interval1[0]:
        if month == interval2[0]:
            if day < interval1[1] and day >= interval2[1]:
                return True
            else:
                return False
        elif month > interval2[0]:
            if day < interval1[1]:
                return True
            else:
                return False
    else:
        if month == interval2[0]:
            if day >= interval2[1]:
                return True
            else:
                return False
        elif month > interval2[0]:
            return True
    return False

def getAverageUserBuy(topk):
    data = [feature for feature in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [map(int, feature) for feature in data[1:]]

    user_average_buy = {}
    if topk == 0:
        user_buy = {}
        for entry in data:
            action_type = entry[2]
            if action_type == settings["ACTION_BUY"]:
                uid = entry[0]
                pid = entry[1]
                month = entry[3]
                day = entry[4]
                segnum = calSegNum(month, day)
                if uid in user_buy:
                    user_buy[uid][0].add(pid)
                    user_buy[uid][1].add(segnum)
                else:
                    user_buy[uid] = [set([pid]), set([segnum])]

        for uid in user_buy:
            user_average_buy[uid] = (len(user_buy[uid][0])+len(user_buy[uid][1])-1)/len(user_buy[uid][1])

    else:
        for entry in data:
            uid = entry[0]
            action_type = entry[2]
            if action_type == settings["ACTION_BUY"]:
                if uid not in user_average_buy:
                    user_average_buy[uid] = topk
    return user_average_buy


def combineFeature(data1, data2):
    return [entry1+entry2 for entry1, entry2 in zip(data1, data2)]


def calMonthLength(month, day):
    day_dif = 0
    if month == 4:
        day_dif = day - 14
    else:
        day_dif = 16 + day
        if month > 5:
            day_dif += 31
        if month > 6:
            day_dif += 30
        if month > 7:
            day_dif += 31
    return 1.0*day_dif/30


def getTimeSegNode(month, day):
    start_month = 4
    start_day = 15

    time_seg_node = []
    while True:
        if month - 1 < 4:
            time_seg_node.append((month, day))
            time_seg_node.append((start_month, start_day))
            break
        elif month - 1 == 4 and day < 15:
            time_seg_node.append((month, day))
            time_seg_node.append((start_month, start_day))
            break
        else:
            time_seg_node.append((month, day))
            month = month - 1
    return time_seg_node


def getDayDiff(month1, day1, month2, day2):
    d1 = datetime.date(settings["TIME_OF_YEAR"], month1, day1)
    d2 = datetime.date(settings["TIME_OF_YEAR"], month2, day2)
    day_diff = d1 - d2
    return day_diff.days


def getUserBehavior(data):
    user_behavior = {}
    for entry in data:
        uid, pid, action_type, month, day = entry
        if uid not in user_behavior:
            user_behavior[uid] = [[], [], []]
        if action_type == 1:
            user_behavior[uid][0].append([pid, month, day])
        elif action_type == 2 or action_type == 3:
            user_behavior[uid][1].append([pid, month, day])
        elif action_type == 0:
            user_behavior[uid][2].append([pid, month, day])
    return user_behavior


def rZero(k):
    return [0.0 for i in range(k)]


def rGaussian(k):
    factor = [random.normalvariate(0, 0.01) for i in xrange(k)]
    for i in xrange(len(factor)):
        if factor[i] > 1:
            factor[i] = 1
        elif factor[i] < -1:
            factor[i] = -1
    return factor


def logisticLoss(pos_score, neg_score):
    return (1-1.0/(1+math.exp(-(pos_score-neg_score))))


if __name__ == "__main__":
    print getTimeSegNode(7,18)
    print calMonthLength(6,16)
