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
# baseline: recommend products users broughted                    #
###################################################################

import sys, csv, json, argparse
from collections import defaultdict
from data_io import write_submission
from tool import getAverageUserBuy

settings = json.loads(open("../SETTINGS.json").read())


def genUserBoughtWithoutSort(train_file):
    data = [feature for feature in csv.reader(open(train_file))]
    data = [map(int, feature) for feature in data[1:]]

    user_bought = defaultdict(set)
    for entry in data:
        action_type = entry[2]
        if action_type == settings["ACTION_BUY"]:
            uid = entry[0]
            pid = entry[1]
            user_bought[uid].add(pid)
    return user_bought


def genUserBoughtBySort(train_file):
    data = [feature for feature in csv.reader(open(train_file))]
    data = [map(int, feature) for feature in data[1:]]

    user_bought = defaultdict(dict)
    for entry in data:
        action_type = entry[2]
        if action_type == settings["ACTION_BUY"]:
            uid = entry[0]
            pid = entry[1]
            if pid in user_bought[uid]:
                user_bought[uid][pid] = 1
            else:
                user_bought[uid][pid] += 1

    user_bought_sort = defaultdict()
    for uid in user_bought:
        temp = sorted(user_bought[uid].items(), key=lambda x:x[1], reverse=True)
        user_bought_sort[uid] = [item[0] for item in temp]

    return user_bought_sort


def genRecommendResult(user_bought_sort, user_average_buy):
    recommend_result = defaultdict(list)
    for uid in user_average_buy:
        topk = user_average_buy[uid]
        recommend_result[uid] = user_bought_sort[uid][0:topk]
    return recommend_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=bool, action='store', dest='tag',
            help='specify whether to consider the user\'s purchasing power.')

    if len(sys.argv) != 3:
        print 'Command e.g.: python runHasBoughted -c True(False)'
        sys.exit(1)

    para = parser.parse_args()
    if not para.tag:
        user_bought = genUserBoughtWithoutSort(settings["TRAIN_DATA_FILE"])
        write_submission(user_bought)
    else:
        user_bought_sort = genUserBoughtBySort(settings["TRAIN_DATA_FILE"])
        user_average_buy = getAverageUserBuy(0)
        recommend_result = genRecommendResult(user_bought_sort, user_average_buy)
        write_submission(recommend_result)


if __name__ == "__main__":
    main()
