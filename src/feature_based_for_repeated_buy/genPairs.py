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
# Generating (user,product) pairs for training on validation      #
#   or test dataset                                               #
###################################################################

import sys, csv, json, argparse, random
sys.path.append("../")
from collections import defaultdict
from tool import calSegNum, getUserBuyByMonth, getUserBehaviorByMonth

settings = json.loads(open("../../SETTINGS.json").read())


def basicGenTrainPair(month_num, user_buy, user_behavior):
    ''' Only considering buy action '''
    pairs = []
    targets = []
    for uid in user_buy:
        for i in xrange(1, month_num):
            for pid in user_buy[uid][i]:
                pairs.append([uid, pid, i+1])
                targets.append([1])
            tmp_behavior = set([])
            for j in xrange(0, i):
                tmp_behavior = tmp_behavior | user_behavior[uid][j]
            for pid in tmp_behavior:
                if pid not in user_buy[uid][i]:
                    pairs.append([uid, pid, i+1])
                    targets.append([0])
    return pairs, targets


def genTestPair(month_num, user_behavior):
    test_pairs = []
    for uid in user_behavior:
        tmp_pid_set = set([])
        for i in xrange(month_num):
            for pid in user_behavior[uid][i]:
                tmp_pid_set.add(pid)
        for pid in tmp_pid_set:
            test_pairs.append([uid, pid, month_num+1])
    return test_pairs


def getHistorySet(user_history, month, day):
    history_set = set([])
    for entry in user_history:
        pid = entry[0]
        h_month = entry[1]
        h_day = entry[2]
        if h_month == month and h_day < day:
            history_set.add(pid)
        elif h_month < month:
            history_set.add(pid)
    return history_set

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=int, action='store',
            dest='target', help='for validation or test dataset')

    if len(sys.argv) != 3:
        print 'Command e.g.: python genPairs.py -t 0(1)'
        sys.exit(1)

    para = parser.parse_args()
    if para.target == 0:
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
        user_buy = getUserBuyByMonth(data, settings["VALIDATION_MONTH_NUM"])
        user_behavior = getUserBehaviorByMonth(data, settings["VALIDATION_MONTH_NUM"])
        pairs, targets = basicGenTrainPair(settings["VALIDATION_MONTH_NUM"], user_buy, user_behavior)
        output_result = [pair+target for pair, target in zip(pairs, targets)]
        writer = csv.writer(open(settings["GBT_TRAIN_PAIR_FOR_VALIDATION"], "w"), lineterminator="\n")
        writer.writerows(output_result)
    elif para.target == 1:
        data = [entry for entry in csv.reader(settings["TAR_DATA_FILE"])]
        data = [map(int, entry) for entry in data[1:]]
        user_buy = getUserBuyByMonth(data, settings["TEST_MONTH_NUM"])
        user_behavior = getUserBehaviorByMonth(data, settings["TEST_MONTH_NUM"])
        pairs, targets = basicGenTrainPair(settings["TEST_MONTH_NUM"], user_buy, user_behavior)
        output_result = [pair+target for pair, target in zip(pairs, targets)]
        writer = csv.writer(open(settings["GBT_TRAIN_PAIR_FOR_TEST"], "w"), lineterminator="\n")
        writer.writerows(output_result)
    elif para.target == 2:
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
        user_behavior = getUserBehaviorByMonth(data, settings["VALIDATION_MONTH_NUM"])
        pairs = genTestPair(settings["VALIDATION_MONTH_NUM"], user_behavior)
        writer = csv.writer(open(settings["GBT_TEST_PAIR_FOR_VALIDATION"], "w"), lineterminator="\n")
        writer.writerows(pairs)
    elif para.target == 3:
        data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
        user_behavior = getUserBehaviorByMonth(data, settings["TEST_MONTH_NUM"])
        pairs = genTestPair(settings["TEST_MONTH_NUM"], user_behavior)
        writer = csv.writer(open(settings["GBT_TEST_PAIR_FOR_TEST"], "w"), lineterminator="\n")
        writer.writerows(pairs)
    else:
        print 'Invalid parameter settings...'
        sys.exit(1)


if __name__ == "__main__":
    main()
