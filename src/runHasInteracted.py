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
# Date: 2014/3/29                                                 #
# baseline: recommend products users have interacted              #
###################################################################

import sys, csv, json, argparse
from collections import defaultdict
from data_io import write_submission

settings = json.loads(open("../SETTINGS.json").read())


def getUserPreference(click_score, collect_score, buy_score):
    #data = [feature for feature in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [feature for feature in csv.reader(open(settings["TAR_DATA_FILE"]))]
    data = [map(int, feature) for feature in data[1:]]

    user_preference_score = defaultdict(dict)
    user_sorted_result = defaultdict(list)
    for entry in data:
        uid, pid, action_type = entry[:3]
        if pid not in user_preference_score[uid]:
            user_preference_score[uid][pid] = 0
        if action_type == settings["ACTION_BUY"]:
            user_preference_score[uid][pid] += buy_score
        elif action_type == settings["ACTION_COLLECT"] or action_type == settings["ACTION_SHOPPING_CHART"]:
            user_preference_score[uid][pid] += collect_score
        elif action_type == settings["ACTION_CLICK"]:
            user_preference_score[uid][pid] += click_score
    for uid in user_preference_score:
        user_sorted_result[uid] = sorted(user_preference_score[uid].items(), key=lambda x:x[1], reverse=True)
    return user_sorted_result


def genRecommendResultByThreshold(user_sorted_result, threshold_value):
    recommend_result = defaultdict(list)
    for uid in user_sorted_result:
        for entry in user_sorted_result[uid]:
            if entry[1] >= threshold_value:
                recommend_result[uid].append(entry[0])
            else:
                break
    return recommend_result


def genRecommendResultByTopK(user_sorted_result, topk):
    recommend_result = defaultdict(list)
    for uid in user_sorted_result:
        tmp = [entry[0] for entry in user_sorted_result[uid]]
        recommend_result[uid] = tmp[:topk]
    return recommend_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s1', type=int, action='store', dest='click_score',
            help='specify the score of user click behavior.')
    parser.add_argument('-s2', type=int, action='store', dest='collect_score',
            help='specify the score of user click behavior.')
    parser.add_argument('-s3', type=int, action='store', dest='buy_score',
            help='specify the score of user click behavior.')
    parser.add_argument('-ts', type=int, action='store', dest='threshold_value',
            help='specify the threshold value.')

    if len(sys.argv) != 9:
        print 'Command e.g.: python runHasInteracted.py -s1 1 -s2 2 -s3 3 -ts 5'
        sys.exit(1)

    para = parser.parse_args()
    user_sorted_result = getUserPreference(para.click_score, para.collect_score, para.buy_score)
    #for uid in user_sorted_result:
    #    print user_sorted_result[uid][:20]
    #    raw_input()
    recommend_result = genRecommendResultByThreshold(user_sorted_result, para.threshold_value)
    #recommend_result = genRecommendResultByTopK(user_sorted_result, 1)
    write_submission(recommend_result)


if __name__ == "__main__":
    main()

