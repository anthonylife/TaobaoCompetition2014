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
# Compute the precision, recall and F-score for evaluation        #
###################################################################

import os, csv, sys, json, argparse
from collections import defaultdict
from data_io import write_submission
from tool import getAverageUserBuy

settings = json.loads(open("../SETTINGS.json").read())
test_ins_file = "./libmf-1.0/testdata.dat"
result_file = "./libmf-1.0/output.dat"
traindata_convert_cmd = "./libmf-1.0/libmf convert " + \
        settings["LIBMF_TRAIN_FILE"] + " ./libmf-1.0/traindata.bin"
testdata_convert_cmd = "./libmf-1.0/libmf convert " + test_ins_file + \
        " ./libmf-1.0/testdata.bin"
train_cmd = "./libmf-1.0/libmf train --tr-rmse --obj -k 40 -t 200 -s 1 -p 0.05 -q 0.05 -g 0.03 -blk 1x1 -ub 1 -ib 1 --use-avg --no-rand-shuffle ./libmf-1.0/traindata.bin ./libmf-1.0/tr.model"
test_cmd = "./libmf-1.0/libmf predict ./libmf-1.0/testdata.bin ./libmf-1.0/tr.model " + result_file

settings = json.loads(open("../SETTINGS.json").read())


def genTestFile(train_file):
    uid_set = set([])
    pid_set = set([])
    data = [feature for feature in csv.reader(open(train_file))]
    data = [map(int, feature) for feature in data[1:]]

    for entry in data:
        uid = entry[0]
        pid = entry[1]
        uid_set.add(uid)
        pid_set.add(pid)
    wfd = open(test_ins_file, "w")
    for uid in uid_set:
        for pid in pid_set:
            wfd.write("%d %d %f\n" % (uid, pid, 0.0))
    wfd.close()


def genTrainFile(train_file, formatted_train_file):
    uid_set = set([])
    pid_set = set([])
    data = [feature for feature in csv.reader(open(train_file))]
    data = [map(int, feature) for feature in data[1:]]

    user_buy = defaultdict(set)
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        uid_set.add(uid)
        pid_set.add(pid)
        action_type = entry[2]
        if action_type == settings["ACTION_BUY"]:
            user_buy[uid].add(pid)

    wfd = open(formatted_train_file, "w")
    for uid in uid_set:
        for pid in pid_set:
            if pid in user_buy[uid]:
                wfd.write("%d %d 1\n" % (uid, pid))
            else:
                wfd.write("%d %d 0\n" % (uid, pid))


def collectUserPreferencePred():
    user_preference_sort = defaultdict(list)
    temp = []
    prev_uid = -1
    for entry1, entry2 in zip(open(test_ins_file), open(result_file)):
        uid = int(entry1.strip("\n\r\t").split(" ")[0])
        pid = int(entry1.strip("\n\r\t").split(" ")[1])
        rating = float(entry2.strip("\n\r\t"))
        if uid != prev_uid:
            temp_result = sorted(temp, key=lambda x:x[1], reverse=True)
            sorted_pid = [entry[0] for entry in temp_result]
            user_preference_sort[uid] = sorted_pid
            temp = []
            prev_uid = uid
        temp.append([pid, rating])
    temp_result = sorted(temp, key=lambda x:x[1], reverse=True)
    sorted_pid = [entry[0] for entry in temp_result]
    user_preference_sort[prev_uid] = sorted_pid
    return user_preference_sort


def genRecommendResult(user_preference_sort, user_average_buy):
    recommend_result = defaultdict(list)
    for uid in user_average_buy:
        topk = user_average_buy[uid]
        recommend_result[uid] = user_preference_sort[uid][0:topk]
    return recommend_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-retrain', type=bool, action='store', dest='retraintag',
            help='specify whether to retrain.')
    parser.add_argument('-topk', type=int, action='store', dest='topk',
            help='specify the number of products to be recommended to\
                    users, 0 stands for using user personal average.')

    if len(sys.argv) != 5:
        print 'Command e.g.: python runLibmf.py -retrain False -topk 5'
        sys.exit(1)
    para = parser.parse_args()

    if para.retraintag:
        genTrainFile(settings["TRAIN_DATA_FILE"], settings["LIBMF_TRAIN_FILE"])
        genTestFile(settings["TRAIN_DATA_FILE"])
        os.system(traindata_convert_cmd)
        os.system(testdata_convert_cmd)
        os.system(train_cmd)
        os.system(test_cmd)
    user_preference_sort = collectUserPreferencePred()
    user_average_buy = getAverageUserBuy(para.topk)
    recommend_result = genRecommendResult(user_preference_sort, user_average_buy)
    write_submission(recommend_result)


if __name__ == "__main__":
    main()
