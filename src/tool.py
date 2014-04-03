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
import numpy as np
from collections import defaultdict

settings = json.loads(open("/home/anthonylife/Doctor/Code/Competition/taobao2014/SETTINGS.json").read())

MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ACTION_NUM = 3

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


def getIdxFromTimeInterval(month, day, last_month, last_day, date_interval_length):
    day_diff = getDayDiff(month, day, last_month, last_day)
    if day_diff < 0 or day_diff >= date_interval_length:
        return -1
    return day_diff


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


def getLastDay(month, day):
    last_month = -1
    last_day = -1
    if day == 1:
        last_month = month-1
        last_day = MONTH[last_month-1]
    else:
        last_month = month
        last_day = day-1
    return last_month, last_day


def getLastWeek(month, day):
    if day > 7:
        day = day - 7
    else:
        month = month - 1
        day = MONTH[month-1]+1-day
    return month, day


def getLastHalfMonth(month, day):
    if day > 15:
        day = day - 15
    else:
        month = month - 1
        day = MONTH[month-1]+1-day
    return month, day


def getLastDate(month, day, day_length):
    if day > day_length:
        day = day - day_length
    else:
        month = month - 1
        day = MONTH[month-1]+1-day
    return month, day


def getLastDayBySegnum(seg_num):
    if seg_num == 2:
        return 5, 14
    elif seg_num == 3:
        return 6, 14
    elif seg_num == 4:
        return 7, 14
    elif seg_num == 5:
        return 8, 15
    else:
        print 'Seg num invalid!'
        sys.exit(1)


def getLastWeekBySegnum(seg_num):
    if seg_num == 2:
        return 5, 8
    elif seg_num == 3:
        return 6, 8
    elif seg_num == 4:
        return 7, 8
    elif seg_num == 5:
        return 8, 9
    else:
        print 'Seg num invalid!'
        sys.exit(1)


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


def getUserBuyByMonth(data, month_num):
    user_behavior = {}
    for entry in data:
        uid, pid, action_type, month, day = entry
        if uid not in user_behavior:
            user_behavior[uid] = [set([]) for i in xrange(month_num)]
        if action_type == 1:
            seg_num = calSegNum(month, day)
            user_behavior[uid][seg_num-1].add(pid)
    return user_behavior


def getUserBehaviorByMonth(data, month_num):
    user_behavior = {}
    for entry in data:
        uid, pid, action_type, month, day = entry
        if uid not in user_behavior:
            user_behavior[uid] = [set([]) for i in xrange(month_num)]
        seg_num = calSegNum(month, day)
        user_behavior[uid][seg_num-1].add(pid)
    return user_behavior


def genDayUPfeature(one_user_behavior, src_pid, last_month, last_day):
    feature = [0 for i in xrange(ACTION_NUM*2)]
    for i in xrange(ACTION_NUM):
        for entry in one_user_behavior[i]:
            pid, month, day = entry
            if pid == src_pid and month == last_month and day == last_day:
                feature[i] = 1
                feature[i+ACTION_NUM] += 1
    return feature


def genMonthUPfeature(one_user_behavior, src_pid, src_seg_num):
    feature = [0 for i in xrange(ACTION_NUM*2)]
    for i in xrange(ACTION_NUM):
        for entry in one_user_behavior[i]:
            pid, month, day = entry
            seg_num = calSegNum(month, day)
            if pid == src_pid and seg_num == src_seg_num:
                feature[i] = 1
                feature[i+ACTION_NUM] += 1
    return feature


def genMonthUPfeature1(one_user_behavior, src_pid, src_month, src_day, last_month, last_day):
    feature = [0 for i in xrange(ACTION_NUM*2)]
    #feature = [0 for i in xrange(ACTION_NUM)]
    for i in xrange(ACTION_NUM):
        for entry in one_user_behavior[i]:
            pid, month, day = entry
            if pid == src_pid and inTimeInterval(month, day, [src_month, src_day],
                    [last_month, last_day]):
                feature[i] = 1
                feature[i+ACTION_NUM] += 1
    return feature


def genHistoryUPfeature(one_user_behavior, src_pid, src_month, src_day):
    feature = [0 for i in xrange(ACTION_NUM*2)]
    for i in xrange(ACTION_NUM):
        for entry in one_user_behavior[i]:
            pid, month, day = entry
            if month < src_month or (month==src_month and day < src_day):
                feature[i] = 1
                feature[i+ACTION_NUM] += 1
    return feature


def genAnyDateIntervalUPfeature(one_user_behavior, src_pid, src_month, src_day, last_month, last_day, date_interval_length):
    feature = [0 for i in xrange(ACTION_NUM*date_interval_length)]
    for i in xrange(ACTION_NUM):
        for entry in one_user_behavior[i]:
            pid, month, day = entry
            if pid != src_pid:
                continue
            idx = getIdxFromTimeInterval(month, day, last_month, last_day, date_interval_length)
            if idx >= 0:
                feature[idx+i*date_interval_length] = 1
                feature[idx+i*date_interval_length] += 1
    return feature


def genProductFeature(one_product_popularity, src_month, src_day, last_month, last_day):
    feature = [0 for i in xrange(ACTION_NUM)]
    for i in xrange(ACTION_NUM):
        for time_key in one_product_popularity[i]:
            month = time_key / 100
            day = time_key % 100
            if inTimeInterval(month, day, [src_month, src_day], [last_month, last_day]):
                feature[i] += one_product_popularity[i][time_key]
    return feature


def getCFfeature(feature_file):
    cf_feature = defaultdict(dict)
    for entry in csv.reader(open(feature_file)):
        uid, pid = map(int, entry[:2])
        score = float(entry[2])
        cf_feature[uid][pid] = score
    return cf_feature


def getProductPopularity(data):
    product_popularity = {}
    for entry in data:
        uid, pid, action_type, month, day = entry
        if pid not in product_popularity:
            product_popularity[pid] = [{}, {}, {}]
        if action_type == 1:
            if month*100+day not in product_popularity[pid][0]:
                product_popularity[pid][0][month*100+day] = 1
            else:
                product_popularity[pid][0][month*100+day] += 1
        elif action_type == 2 or action_type == 3:
            if month*100+day not in product_popularity[pid][1]:
                product_popularity[pid][1][month*100+day] = 1
            else:
                product_popularity[pid][1][month*100+day] += 1
        elif action_type == 0:
            if month*100+day not in product_popularity[pid][2]:
                product_popularity[pid][2][month*100+day] = 1
            else:
                product_popularity[pid][2][month*100+day] += 1
    return product_popularity


def getProductBuyClickRatio(data):
    product_history = {}
    user_click_buy = {}
    for entry in data:
        uid, pid, action_type, month, day = entry
        if action_type == 0:
            if pid not in product_history:
                product_history[pid] = [set([]), set([])]
            product_history[pid][0].add(uid)
            if uid not in user_click_buy:
                user_click_buy[uid] = [{}, {}]
            if pid not in user_click_buy[uid][0]:
                user_click_buy[uid][0][pid] = month*100+day
            else:
                if month*100+day < user_click_buy[uid][0][pid]:
                    user_click_buy[uid][0][pid] = month*100+day
        elif action_type == 1:
            if pid not in product_history:
                product_history[pid] = [set([]), set([])]
            product_history[pid][0].add(uid)
            product_history[pid][1].add(uid)
            if uid not in user_click_buy:
                user_click_buy[uid] = [{}, {}]
            if pid not in user_click_buy[uid][1]:
                user_click_buy[uid][1][pid] = month*100+day
            else:
                if month*100+day > user_click_buy[uid][1][pid]:
                    user_click_buy[uid][1][pid] = month*100+day

    product_ratio1 = {}
    for pid in product_history:
        product_ratio1[pid] = 1.0*len(product_history[pid][1])/len(product_history[pid][0])

    product_ratio2 = {}
    product_history = {}
    for uid in user_click_buy:
        for pid in user_click_buy[uid][0]:
            if pid not in product_history:
                product_history[pid] = [0, 0]
            product_history[pid][0] += 1
            time = user_click_buy[uid][0][pid]
            if pid in user_click_buy[uid][1]:
                if time < user_click_buy[uid][1][pid]:
                    product_history[pid][1] += 1
    for pid in product_history:
        product_ratio2[pid] = 1.0*product_history[pid][1]/product_history[pid][0]

    return product_ratio1, product_ratio2


def getProductBuyBuyRatio(data):
    user_buy_history = defaultdict(dict)
    for entry in data:
        uid, pid, action_type, month, day = entry
        if action_type == 1:
            if pid not in user_buy_history[uid]:
                user_buy_history[uid] = defaultdict(set)
            user_buy_history[uid][pid].add(month*100+day)

    buy_buy_ratio = {}
    buy_buy_cnt = {}
    for uid in user_buy_history:
        for pid in user_buy_history[uid]:
            if pid not in buy_buy_cnt:
                buy_buy_cnt[pid] = [0, 0]
            if len(user_buy_history[uid][pid]) > 1:
                buy_buy_cnt[pid][1] += 1
            buy_buy_cnt[pid][0] += 1
    for pid in buy_buy_cnt:
        buy_buy_ratio[pid] = 1.0*buy_buy_cnt[pid][1]/buy_buy_cnt[pid][0]

    return buy_buy_ratio

def getUserBuyClickRatio(data):
    user_buy_history1 = {}
    user_buy_history2 = {}

    for entry in data:
        uid, pid, action_type, month, day = entry
        if action_type == 1:
            if uid not in user_buy_history1:
                user_buy_history1[uid] = [0, 0]
            if uid not in user_buy_history2:
                user_buy_history2[uid] = [set([]), set([])]
            user_buy_history1[uid][1] += 1
            user_buy_history2[uid][1].add(pid)
        elif action_type == 0:
            if uid not in user_buy_history1:
                user_buy_history1[uid] = [0, 0]
            if uid not in user_buy_history2:
                user_buy_history2[uid] = [set([]), set([])]
            user_buy_history1[uid][0] += 1
            user_buy_history2[uid][0].add(pid)

    user_buy_click_ratio = {}
    for uid in user_buy_history1:
        if uid not in user_buy_click_ratio:
            user_buy_click_ratio[uid] = [0.0, 0.0]
        if user_buy_history1[uid][1] != 0:
            user_buy_click_ratio[uid][0] = 1.0*user_buy_history1[uid][0]/user_buy_history1[uid][1]
            user_buy_click_ratio[uid][1] = 1.0*len(user_buy_history2[uid][0])/len(user_buy_history2[uid][1])
        elif user_buy_history1[uid][0] == 0:
            user_buy_click_ratio[uid][0] = 0.0
            user_buy_click_ratio[uid][1] = 0.0
        else:
            user_buy_click_ratio[uid][0] = 1.0
            user_buy_click_ratio[uid][1] = 1.0
    return user_buy_click_ratio


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


def rPosGaussian(k):
    factor = [random.normalvariate(0, 0.01) for i in xrange(k)]
    for i in xrange(len(factor)):
        if factor[i] > 1:
            factor[i] = 1
        elif factor[i] < -1:
            factor[i] = -1
        factor[i] = (factor[i]+1)/2.0
    return factor


def logisticLoss(pos_score, neg_score):
    return (1-1.0/(1+math.exp(-(pos_score-neg_score))))


def underSampling(features, ratio):
    pos_features = []
    neg_features = []
    for feature in features:
        if feature[-1] == 1:
            pos_features.append(feature)
        else:
            neg_features.append(feature)
    random.shuffle(neg_features)
    neg_features = neg_features[:ratio*len(pos_features)]
    features = pos_features + neg_features
    random.shuffle(features)
    return features


def load_factor_model(model_path):
    factor = {}
    for entry in csv.reader(open(model_path)):
        tid = int(entry[0])
        factor[tid] = np.array(map(float, entry[1:]))
    return factor


if __name__ == "__main__":
    print getTimeSegNode(7,18)
    print calMonthLength(6,16)
