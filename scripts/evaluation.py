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

import sys, csv, json, argparse
from collections import defaultdict

settings = json.loads(open("../SETTINGS.json").read())


def readTestResult(tFile):
    data = [feature for feature in csv.reader(open(tFile))]
    data = [map(int, feature) for feature in data[1:]]

    std_result = defaultdict(set)
    for feature in data:
        action_type = feature[2]
        if action_type == settings["ACTION_BUY"]:
            uid = feature[0]
            pid = feature[1]
            std_result[uid].add(pid)
    return std_result


def readPredResult(pFile):
    pred_result = defaultdict(set)
    for entry in open(pFile):
        uid = int(entry.split("\t")[0])
        products = entry.split("\t")[1]
        for product in products.split(","):
            pred_result[uid].add(int(product))
    return pred_result


def evaluation(std_result, pred_result):
    # calculate precision
    sum_pred_num = 0
    true_pred_num = 0
    for uid in pred_result:
        if uid in std_result:
            true_pred_num += len(std_result[uid] & pred_result[uid])
        sum_pred_num += len(pred_result[uid])
    if sum_pred_num != 0:
        precision = (1.0*true_pred_num)/sum_pred_num
    else:
        precision = 0.0

    # calculate recall
    sum_true_num = 0
    true_pred_num = 0
    for uid in std_result:
        if uid in pred_result:
            true_pred_num += len(std_result[uid] & pred_result[uid])
        sum_true_num += len(std_result[uid])
    recall = (1.0*true_pred_num)/sum_true_num

    # calculate F-score
    if (precision + recall) == 0:
        FScore = 0
    else:
        FScore = (2*precision*recall)/(precision+recall)
    print true_pred_num, sum_pred_num, sum_true_num
    return [FScore, precision, recall]


def getUserBought():
    data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]

    user_bought = defaultdict(set)
    for entry in data:
        uid, pid, action_type = entry[:3]
        if action_type == 1:
            user_bought[uid].add(pid)
    return user_bought


def getUserAction():
    data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]

    user_bought = defaultdict(set)
    for entry in data:
        uid, pid, action_type = entry[:3]
        user_bought[uid].add(pid)
    return user_bought


def removeAlreadyAction(user_behavior, std_result, pred_result):
    for uid in user_behavior:
        if uid in std_result:
            std_result[uid] = std_result[uid]-user_behavior[uid]
        if uid in pred_result:
            pred_result[uid] = pred_result[uid]-user_behavior[uid]
    return std_result, pred_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pFile', type=str, action='store', dest='pFile',
            help='specify the file of prediction results')
    parser.add_argument('-tFile', type=str, action='store', dest='tFile',
            help='specify the file of standard test results')

    if len(sys.argv) != 5:
        print 'Command e.g.: python evaluation.py -pFile <str> -tFile <str>'
        sys.exit(1)

    para = parser.parse_args()
    std_result = readTestResult(para.tFile)
    pred_result = readPredResult(para.pFile)

    [FScore, precision, recall] = evaluation(std_result, pred_result)
    print 'Evaluation on test data: F-score-->%f, precision-->%f, recall-->%f' % (FScore, precision, recall)

    user_bought = getUserBought()
    std_result, pred_result = removeAlreadyAction(user_bought, std_result, pred_result)
    [FScore, precision, recall] = evaluation(std_result, pred_result)
    print 'Evaluation on test data for not buy products: F-score-->%f, precision-->%f, recall-->%f' % (FScore, precision, recall)

    user_behavior = getUserAction()
    std_result, pred_result = removeAlreadyAction(user_behavior, std_result, pred_result)
    [FScore, precision, recall] = evaluation(std_result, pred_result)
    print 'Evaluation on test data for not action products: F-score-->%f, precision-->%f, recall-->%f' % (FScore, precision, recall)


if __name__ == "__main__":
    main()
