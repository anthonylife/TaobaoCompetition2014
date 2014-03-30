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

import sys, csv, json, argparse, random, time
sys.path.append("../")
import numpy as np
from collections import defaultdict
from tool import combineFeature, calSegNum, calMonthLength

settings = json.loads(open("../../SETTINGS.json").read())
TOTAL_MONTH = 3

def genTestPairForBuy(data):
    uid_set = set([])
    pid_set = set([])
    for entry in data:
        uid = int(entry[0])
        pid = int(entry[1])
        uid_set.add(uid)
        pid_set.add(pid)
    test_pairs = []
    for uid in uid_set:
        for pid in pid_set:
            #test_pairs.append([uid, pid, settings["TIME_LAST_MONTH"], settings["TIME_LAST_DAY"]])
            test_pairs.append([uid, pid])
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
        user_behavior[uid][pid].append([action_type, month, day])
    return user_behavior


def getProductAction(data):
    product_behavior = {}
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        action_type = entry[2]
        month = entry[3]
        day = entry[4]
        if pid not in product_behavior:
            product_behavior[pid] = defaultdict(list)
        product_behavior[pid][uid].append([action_type, month, day])
    return product_behavior


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
    user_bought = {}
    for uid in user_behavior:
        user_bought[uid] = [0.0 for i in xrange(4)]
        total_num = [0 for i in xrange(TOTAL_MONTH)]
        product_set = [set([]) for i in xrange(TOTAL_MONTH)]
        for pid in user_behavior[uid]:
            for entry in user_behavior[uid][pid]:
                if entry[0] == 1:
                    seg_num = calSegNum(entry[1], entry[2])
                    product_set[seg_num-1].add(pid)
                    total_num[seg_num-1]+= 1
        for i in xrange(TOTAL_MONTH):
            user_bought[uid][0] += len(product_set[i])
            user_bought[uid][2] += total_num[i]
        user_bought[uid][1] = float(user_bought[uid][0])/TOTAL_MONTH
        user_bought[uid][0] = len(product_set[TOTAL_MONTH-1])
        user_bought[uid][3] = float(user_bought[uid][2])/TOTAL_MONTH
        user_bought[uid][2] = total_num[TOTAL_MONTH-1]


    product_behavior = getProductAction(data)
    product_bought = {}
    for pid in product_behavior:
        product_bought[pid] = [0.0 for i in xrange(4)]
        total_num = [0 for i in xrange(TOTAL_MONTH)]
        user_set = [set([]) for i in xrange(TOTAL_MONTH)]
        for uid in product_behavior[pid]:
            for entry in product_behavior[pid][uid]:
                if entry[0] == 1:
                    seg_num = calSegNum(entry[1], entry[2])
                    user_set[seg_num-1].add(uid)
                    total_num[seg_num-1] += 1
        for i in xrange(TOTAL_MONTH):
            product_bought[pid][0] += len(user_set[i])
            product_bought[pid][2] = total_num[i]
        product_bought[pid][1] = float(product_bought[pid][0])/TOTAL_MONTH
        product_bought[pid][0] = len(user_set[TOTAL_MONTH-1])
        product_bought[pid][3] = float(product_bought[pid][2])/TOTAL_MONTH
        product_bought[pid][2] = total_num[TOTAL_MONTH-1]

    data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]
    test_pairs = genTestPairForBuy(data)
    user_behavior = getUserAction(data)
    writer = csv.writer(open(settings["GBT_TEST_FILE"], "w"), lineterminator="\n")

    output_feature = [0 for i in range(59)]
    score = 0.0
    d_day = 14
    d_month = 7
    w_day = 8
    w_month = 7
    m_day = 14
    m_month = 6
    tmp_cnt = np.array([0 for i in range(16)])

    print "Start generating features...."
    a = time.clock()
    for ii, pair in enumerate(test_pairs):
        uid = pair[0]
        pid = pair[1]
        output_feature[0] = uid
        output_feature[1] = pid

        if para.tCF == 1:
            if pid not in product_factor:
                score = 0.0
            elif uid not in user_factor:
                score = 0.0
            else:
                score = np.dot(user_factor[uid], product_factor[pid])
            output_feature[2] = score

        if para.tUP == 1:
            for entry in user_behavior[uid][pid]:
                action_type = entry[0]
                src_month = entry[1]
                src_day = entry[2]
                if src_month == d_month:
                    if src_day == d_day:
                        output_feature[3+action_type*3] = 1
                        output_feature[3+action_type*3+1] += 1
                        tmp_cnt[action_type] += 1
                        output_feature[15+action_type*3] = 1
                        output_feature[15+action_type*3+1] += 1
                        tmp_cnt[4+action_type] += 1
                    elif w_day <= src_day:
                        output_feature[15+action_type*3] = 1
                        output_feature[15+action_type*3+1] += 1
                        tmp_cnt[4+action_type] += 1
                    output_feature[27+action_type*3] = 1
                    output_feature[27+action_type*3+1] += 1
                    tmp_cnt[8+action_type] += 1
                elif src_month == m_month and src_day > m_day:
                    output_feature[27+action_type*3] = 1
                    output_feature[27+action_type*3+1] += 1
                    tmp_cnt[8+action_type] += 1
                output_feature[39+action_type*3] = 1
                output_feature[39+action_type*3+1] += 1
                tmp_cnt[12+action_type] += 1
            for i in xrange(16):
                if tmp_cnt[i] == 0:
                    output_feature[5+i*3] = 0
                else:
                    output_feature[5+i*3] = float(output_feature[5+i*3])/tmp_cnt[i]
                tmp_cnt[i] = 0

        if para.tU == 1:
            if uid not in user_bought:
                output_feature[51] = 0
                output_feature[52] = 0
                output_feature[53] = 0
                output_feature[54] = 0
            else:
                output_feature[51] = user_bought[uid][0]
                output_feature[52] = user_bought[uid][1]
                output_feature[53] = user_bought[uid][2]
                output_feature[54] = user_bought[uid][3]

        if para.tP == 1:
            if pid not in product_bought:
                output_feature[55] = 0
                output_feature[56] = 0
                output_feature[57] = 0
                output_feature[58] = 0
            else:
                output_feature[55] = product_bought[pid][0]
                output_feature[56] = product_bought[pid][1]
                output_feature[57] = product_bought[pid][2]
                output_feature[58] = product_bought[pid][3]

        writer.writerow(output_feature)
        output_feature = np.array([0.0 for i in range(59)])
        if ii % 10000 == 0:
            print "\r%d, cost time: %.1f seconds" % (ii, time.clock() - a)
            a = time.clock()

if __name__ == "__main__":
    main()
