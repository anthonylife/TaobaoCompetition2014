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
# Date: 2014/3/18                                                 #
# Make feature for decision/regression method                     #
# Feature lists: 1.Collaborative feture                           #
#                2.User product interaction feature               #
#                3.User feature                                   #
#                4.Product feature                                #
###################################################################

import sys, csv, json, argparse, random
sys.path.append("../")
import numpy as np
from collections import defaultdict
from tool import combineFeature, calSegNum, calMonthLength

settings = json.loads(open("../../SETTINGS.json").read())


def genTrainPairForBuy(ratio, data):
    pid_set = set([])
    user_behavior = defaultdict(set)
    for entry in data:
        pid_set.add(entry[1])
        user_behavior[entry[0]].add(entry[1])

    train_pairs = []
    targets = []
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        action_type = entry[2]
        month = entry[3]
        day = entry[4]
        seg_num = calSegNum(month, day)
        if action_type == 1 and seg_num > 1:
            train_pairs.append([uid, pid, month, day])
            neg_pid_set = random.sample(pid_set-user_behavior[uid], ratio)
            targets.append([1])
            for neg_pid in neg_pid_set:
                train_pairs.append([uid, neg_pid, month, day])
                targets.append([0])
    return train_pairs, targets


def genTestPairForBuy(data):
    uid_set = set([])
    pid_set = set([])
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        uid_set.add(uid)
        pid_set.add(pid)
    test_pairs = []
    for uid in uid_set:
        for pid in pid_set:
            test_pairs.append([uid, pid, settings["TIME_LAST_MONTH"], settings["TIME_LAST_DAY"]])
    return test_pairs


def getUserAction(data):
    user_behavior = {}
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        action_type = entry[2]
        month = entry[3]
        day = entry[4]
        if uid not in user_behavior:
            user_behavior[uid] = defaultdict(list)
        #if pid not in user_behavior[uid]:
        #    user_behavior[uid][pid] = []
        user_behavior[uid][pid].append([action_type, month, day])
    return user_behavior


def getCFfeature(train_pairs, user_factor, product_factor):
    features = []
    for pair in train_pairs:
        uid = pair[0]
        pid = pair[1]
        if pid not in product_factor:
            features.append([0])
        elif uid not in user_factor:
            features.append([0])
        else:
            score = np.dot(user_factor[uid], product_factor[pid])
            features.append([score])
    return features


def getUPfeature(train_pairs, user_behavior):
    features = []
    for pair in train_pairs:
        uid = pair[0]
        pid = pair[1]
        month = pair[2]
        day = pair[3]
        day_feature = genDayUPfeature(user_behavior, uid, pid, month, day)
        week_feature = genWeekUPfeature(user_behavior, uid, pid, month, day)
        month_feature = genMonthUPfeature(user_behavior, uid, pid, month, day)
        history_feature = genHistoryUPfeature(user_behavior, uid, pid, month, day)
        features.append(day_feature+week_feature+month_feature+history_feature)
    return features


def genDayUPfeature(user_behavior, uid, pid, month, day):
    tar_month = -1
    tar_day = -1
    if day == 1:
        tar_month = month-1
        if tar_month % 2 == 1:
            tar_day = 31
        else:
            tar_day = 30
    else:
        tar_month = month
        tar_day = day-1

    tmp_cnt = [0 for i in range(4)]
    feature = [0 for i in range(3*4)]
    for entry in user_behavior[uid][pid]:
        src_month = entry[1]
        src_day = entry[2]
        action_type = entry[0]

        if tar_month == src_month and tar_day == src_day:
            feature[action_type*3+0] = 1
            feature[action_type*3+1] += 1
            tmp_cnt[action_type] += 1
    for i in range(4):
        if tmp_cnt[i] == 0:
            feature[i*3+2] = 0.0
        else:
            feature[i*3+2] = float(feature[i*3+1])/tmp_cnt[i]
    return feature


def genWeekUPfeature(user_behavior, uid, pid, month, day):
    tar_month = -1
    tar_day = day - 7
    if tar_day <= 0:
        tar_month = month - 1
        if tar_month % 2 == 1:
            tar_day = 31 + tar_day
        else:
            tar_day = 30 + tar_day
    else:
        tar_month = month

    tmp_cnt = [0 for i in range(4)]
    feature = [0 for i in range(3*4)]
    for entry in user_behavior[uid][pid]:
        src_month = entry[1]
        src_day = entry[2]
        action_type = entry[0]
        if tar_month == month:
            if (tar_month == src_month and tar_day <= src_day and src_day < day):
                feature[action_type*3+0] = 1
                feature[action_type*3+1] += 1
                tmp_cnt[action_type] += 1
        else:
            if (tar_month == src_month and tar_day <= src_day) or (month == src_month and src_day < day):
                feature[action_type*3+0] = 1
                feature[action_type*3+1] += 1
                tmp_cnt[action_type] += 1
    for i in range(4):
        if tmp_cnt[i] == 0:
            feature[i*3+2] = 0.0
        else:
            feature[i*3+2] = float(feature[i*3+1])/tmp_cnt[i]
    return feature


def genMonthUPfeature(user_behavior, uid, pid, month, day):
    tar_month = month - 1
    tar_day = day

    tmp_cnt = [0 for i in range(4)]
    feature = [0 for i in range(3*4)]
    for entry in user_behavior[uid][pid]:
        src_month = entry[1]
        src_day = entry[2]
        action_type = entry[0]
        if (tar_month == src_month and tar_day <= src_day) or\
            (month == src_month and src_day < day):
            feature[action_type*3+0] = 1
            feature[action_type*3+1] += 1
            tmp_cnt[action_type] += 1
    for i in xrange(4):
        if tmp_cnt[i] == 0:
            feature[i*3+2] = 0.0
        else:
            feature[i*3+2] = float(feature[i*3+1])/tmp_cnt[i]
    return feature


def genHistoryUPfeature(user_behavior, uid, pid, month, day):
    tmp_cnt = [0 for i in range(4)]
    feature = [0 for i in range(3*4)]
    for entry in user_behavior[uid][pid]:
        src_month = entry[1]
        src_day = entry[2]
        action_type = entry[0]
        if src_month < month or (src_month == month and src_day < day):
            feature[action_type*3+0] = 1
            feature[action_type*3+1] += 1
            tmp_cnt[action_type] += 1
    for i in xrange(4):
        if tmp_cnt[i] == 0:
            feature[i*3+2] = 0.0
        else:
            feature[i*3+2] = float(feature[i*3+1])/tmp_cnt[i]
    return feature


#def getUfeature(user_behavior, uid, sorted_pid):
    #feature = [0 for i in range(len(2+sorted_pid))]
def getUfeature(train_pairs, user_behavior):
    features = []
    for pair in train_pairs:
        uid = pair[0]
        month = pair[2]
        day = pair[3]
        tar_month = month - 1
        tar_day = day

        feature = [set([]), 0, 0, 0]      #1.last type num;2.ave type num;3.last pro num;4.ave pro num.
        total_type_num = set([])
        total_pro_num = 0
        month_length = calMonthLength(month, day)
        for pid in user_behavior[uid]:
            for entry in user_behavior[uid][pid]:
                action_type = entry[0]
                src_month = entry[1]
                src_day = entry[2]
                if action_type == 1:
                    if src_month < month or (src_month == month and src_day < day):
                        total_type_num.add(pid)
                        total_pro_num+=1
                        if (tar_month == src_month and tar_day <= src_day) or\
                            (month == src_month and src_day < day):
                            feature[0].add(pid)
                            feature[2] += 1
        feature[0] = len(feature[0])
        feature[1] = len(total_type_num)/month_length
        feature[3] = (1.0)*total_pro_num/month_length
        features.append(feature)
    return features


def getPfeature(train_pairs, user_behavior):
    features = []
    for pair in train_pairs:
        pid = pair[1]
        month = pair[2]
        day = pair[3]
        tar_month = month - 1
        tar_day = day

        feature = [set([]), 0, 0, 0]      #1.last person num;2.ave person num;3.last buy num;4.ave buy num.
        total_person_num = set([])
        total_buy_num = 0
        month_length = calMonthLength(month, day)
        for uid in user_behavior:
            for pid in user_behavior[uid]:
                for entry in user_behavior[uid][pid]:
                    action_type = entry[0]
                    src_month = entry[1]
                    src_day = entry[2]
                    if action_type == 1:
                        if src_month < month or (src_month == month and src_day < day):
                            total_person_num.add(uid)
                            total_buy_num += 1
                            if (tar_month == src_month and tar_day <= src_day) or\
                                (month == src_month and src_day < day):
                                feature[0].add(uid)
                                feature[2] += 1
        feature[0] = len(feature[0])
        feature[1] = len(total_person_num)/month_length
        feature[3] = (1.0)*total_buy_num/month_length
        features.append(feature)
    return features


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=int, action='store',
            dest='ratio', help='number of negative to positive')
    parser.add_argument('-cf', type=int, action='store',
            dest='tCF', help='whether use collaborative feature')
    parser.add_argument('-up', type=int, action='store',
            dest='tUP', help='whether use user product interaction feature')
    parser.add_argument('-u', type=int, action='store',
            dest='tU', help='whether use user feature')
    parser.add_argument('-p', type=int, action='store',
            dest='tP', help='whether use product feature')

    if len(sys.argv) != 11:
        print 'Command e.g.: python makeFeature.py -r 5 -cf 1(0) -up 1(0) '\
                + '-u 1(0) -p 1(0)'

    para = parser.parse_args()
    user_factor = {}
    for entry in csv.reader(open(settings["MODEL_USER_FILE"])):
        uid = int(entry[0])
        factor = np.array(map(float, entry[1:]))
        user_factor[uid] = factor

    product_factor = {}
    for entry in csv.reader(open(settings["MODEL_PRODUCT_FILE"])):
        pid = int(entry[0])
        factor = np.array(map(float, entry[1:]))
        product_factor[pid] = factor
    data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]

    user_behavior = getUserAction(data)
    train_pairs, targets = genTrainPairForBuy(para.ratio, data)
    output_feature = [[] for i in xrange(len(train_pairs))]
    if para.tCF == 1:
        cf_feature = getCFfeature(train_pairs)
        output_feature = combineFeature(output_feature, cf_feature)
    if para.tUP == 1:
        up_feature = getUPfeature(train_pairs, user_behavior)
        output_feature = combineFeature(output_feature, up_feature)
    if para.tU == 1:
        u_feature = getUfeature(train_pairs, user_behavior)
        output_feature = combineFeature(output_feature, u_feature)
    if para.tP == 1:
        p_feature = getPfeature(train_pairs, user_behavior)
        output_feature = combineFeature(output_feature, p_feature)

    output_feature = combineFeature(output_feature, targets)
    writer = csv.writer(open(settings["GBT_TRAIN_FILE"], "w"), lineterminator="\n")
    writer.writerows(output_feature)

    '''data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]

    test_pairs = genTestPairForBuy(data)
    user_behavior = getUserAction(data)
    writer = csv.writer(open(settings["GBT_TEST_FILE"], "w"), lineterminator="\n")
    for pair in test_pairs:
        output_feature = [pair]
        if para.tCF == 1:
            cf_feature = getCFfeature([pair], user_factor, product_factor)
            output_feature = combineFeature(output_feature, cf_feature)
        if para.tUP == 1:
            up_feature = getUPfeature([pair], user_behavior)
            output_feature = combineFeature(output_feature, up_feature)
        if para.tU == 1:
            u_feature = getUfeature([pair], user_behavior)
            output_feature = combineFeature(output_feature, u_feature)
        if para.tP == 1:
            p_feature = getPfeature([pair], user_behavior)
            output_feature = combineFeature(output_feature, p_feature)
        writer.writerows(output_feature)'''


if __name__ == "__main__":
    main()
