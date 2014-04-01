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
from tool import calSegNum

settings = json.loads(open("../../SETTINGS.json").read())

validation_month = 7
validation_day = 15
test_month = 8
test_day = 16

###################----Basic----####################
# Only using "buy" data
def basicGenTrainPair(data, ratio):
    pid_set = set([])
    user_behavior = defaultdict(list)
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        action_type = entry[2]
        month = entry[3]
        day = entry[4]
        pid_set.add(pid)
        if action_type == 1:
            user_behavior[uid].append([pid, month, day])

    pairs = []
    targets = []
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        action_type = entry[2]
        month = entry[3]
        day = entry[4]
        seg_num = calSegNum(month, day)
        if action_type == 1 and seg_num > 1:
            pairs.append([uid, pid, month, day])
            uid_history_set = getHistorySet(user_behavior[uid], month, day)
            neg_pid_set = random.sample(pid_set-uid_history_set, ratio)
            targets.append([1])
            for neg_pid in neg_pid_set:
                pairs.append([uid, neg_pid, month,day])
                targets.append([0])

    return pairs, targets

###################----Basic----####################


def genTestPair(data, target):
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
            if target == 2:
                test_pairs.append([uid, pid, validation_month, validation_day])
            elif target == 3:
                test_pairs.append([uid, pid, test_month, test_day])
            else:
                print 'target setting error!'
                sys.exit(1)
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
    parser.add_argument('-r', type=int, action='store',
            dest='ratio', help='number of negative to positive')

    if len(sys.argv) != 5:
        print 'Command e.g.: python genPairs.py -t 0(1) -r 5'
        sys.exit(1)

    para = parser.parse_args()
    if para.target == 0:
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
        pairs, targets = basicGenTrainPair(data, para.ratio)
        #pairs, targets = popGenPair(data, para.ratio)
        output_result = [pair+target for pair, target in zip(pairs, targets)]
        writer = csv.writer(open(settings["GBT_TRAIN_PAIR_FOR_VALIDATION"], "w"), lineterminator="\n")
        writer.writerows(output_result)
    elif para.target == 1:
        data = [entry for entry in csv.reader(settings["TAR_DATA_FILE"])]
        data = [map(int, entry) for entry in data[1:]]
        pairs, targets = basicGenTrainPair(data, para.ratio)
        #pairs, targets = popGenPair(data, para.ratio)
        output_result = [pair+target for pair, target in zip(pairs, targets)]
        writer = csv.writer(open(settings["GBT_TRAIN_PAIR_FOR_TEST"], "w"), lineterminator="\n")
        writer.writerows(output_result)
    elif para.target == 2:
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
        pairs = genTestPair(data, para.target)
        writer = csv.writer(open(settings["GBT_TEST_PAIR_FOR_VALIDATION"], "w"), lineterminator="\n")
        writer.writerows(pairs)
    elif para.target == 3:
        data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
        pairs = genTestPair(data, para.target)
        writer = csv.writer(open(settings["GBT_TEST_PAIR_FOR_TEST"], "w"), lineterminator="\n")
        writer.writerows(pairs)
    else:
        print 'Invalid parameter settings...'
        sys.exit(1)


if __name__ == "__main__":
    main()
