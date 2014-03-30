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
# Item-based CF method                                            #
###################################################################

import sys, csv, json, argparse, math
sys.path.append("../")
from collections import defaultdict
from data_io import write_submission

settings = json.loads(open("../../SETTINGS.json").read())

TOP_SIM_NUM = 10
TOPK = 5

def getUserBought(data):
    user_bought = defaultdict(set)
    for entry in data:
        uid, pid, action_type = entry[:3]
        if action_type == 1:
            user_bought[uid].add(pid)
    return user_bought


def getUserBehavior(data):
    user_behavior = {}
    for entry in data:
        uid, pid, action_type = entry[:3]
        if uid not in user_behavior:
            #user_behavior[uid] = [set([]), set([]), set([])]
            user_behavior[uid] = [[], [], []]
        if action_type == 1:
            #user_behavior[uid][0].add(pid)
            user_behavior[uid][0].append(pid)
        elif action_type == 2 or action_type == 3:
            #user_behavior[uid][1].add(pid)
            user_behavior[uid][1].append(pid)
        elif action_type == 0:
            #user_behavior[uid][2].add(pid)
            user_behavior[uid][2].append(pid)
    return user_behavior

def createdInvertedIndex(data):
    ''' Without considering the difference between different actions '''
    user_inverted_index = defaultdict(set)
    for entry in data:
        uid, pid, action_type = entry[:3]
        if action_type == 1:
            user_inverted_index[uid].add(pid)
    return user_inverted_index


def itemSimilarity(user_inverted_index):
    count_matrix = {}
    item_count = defaultdict(set)
    for uid in user_inverted_index:
        for pid1 in user_inverted_index[uid]:
            item_count[pid1].add(uid)
            for pid2 in user_inverted_index[uid]:
                if pid1 == pid2:
                    continue
                if pid1 not in count_matrix:
                    count_matrix[pid1] = {}
                if pid2 not in count_matrix[pid1]:
                    count_matrix[pid1][pid2] = 1
                else:
                    count_matrix[pid1][pid2] += 1
                if pid2 not in count_matrix:
                    count_matrix[pid2] = {}
                if pid1 not in count_matrix[pid2]:
                    count_matrix[pid2][pid1] = 1
                else:
                    count_matrix[pid2][pid1] += 1

    sim_matrix = defaultdict(dict)
    for pid1 in count_matrix:
        for pid2 in count_matrix[pid1]:
            if pid1 == pid2:
                continue
            sim_matrix[pid1][pid2] = count_matrix[pid1][pid2]\
                    /math.sqrt(len(item_count[pid1])*len(item_count[pid2]))

    sim_items = {}
    for pid in sim_matrix:
        sim_sum = sum([entry[1] for entry in sim_matrix[pid].items()])
        tmp_items = sorted(sim_matrix[pid].items(), key=lambda x:x[1], reverse=True)
        #sim_items[pid] = [[entry[0], entry[1]/sim_sum] for entry in tmp_items[:TOP_SIM_NUM]]
        sim_items[pid] = tmp_items[:TOP_SIM_NUM]

    return sim_items


def genRecommendResult(sim_items, user_bought, t_val):
    user_result = defaultdict(dict)
    for uid in user_bought:
        for pid in user_bought[uid]:
            if pid not in sim_items:
                continue
            for entry in sim_items[pid]:
                pid1, score = entry
                #if pid not in user_result[uid]:
                #    user_result[uid][pid] = 1.0
                if pid1 not in user_result[uid]:
                    user_result[uid][pid1] = 0.0
                user_result[uid][pid1] += score

    recommend_result = defaultdict(list)
    for uid in user_result:
        for entry in user_result[uid].items():
            pid, score = entry
            if score > t_val:
                recommend_result[uid].append(pid)

    #for uid in user_result:
    #    tmp_result = sorted(user_result[uid].items(), key=lambda x:x[1], reverse=True)
    #    recommend_result[uid] = [entry[0] for entry in tmp_result[:TOPK]]

    return recommend_result


def genRecommendResult1(sim_items, user_behavior, t_val):
    user_result = defaultdict(dict)
    for uid in user_behavior:
        for pid in user_behavior[uid][0]:
            if pid not in user_result[uid]:
                user_result[uid][pid] = 3.0
            else:
                user_result[uid][pid] += 3.0
            if pid not in sim_items:
                continue
            for entry in sim_items[pid]:
                pid1, score = entry
                if pid1 not in user_result[uid]:
                    user_result[uid][pid1] = 0.0
                user_result[uid][pid1] += 0*score
        for pid in user_behavior[uid][1]:
            if pid not in user_result[uid]:
                user_result[uid][pid] = 2.0
            else:
                user_result[uid][pid] += 2.0
        for pid in user_behavior[uid][2]:
            if pid not in user_result[uid]:
                user_result[uid][pid] = 1.0
            else:
                user_result[uid][pid] += 1.0

    recommend_result = defaultdict(list)
    for uid in user_result:
        for entry in user_result[uid].items():
            pid, score = entry
            if score > t_val:
                recommend_result[uid].append(pid)

    #for uid in user_result:
    #    tmp_result = sorted(user_result[uid].items(), key=lambda x:x[1], reverse=True)
    #    recommend_result[uid] = [entry[0] for entry in tmp_result[:TOPK]]

    return recommend_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tv', type=float, action='store', dest='threshold_val',
            help='specify threshold value.')

    if len(sys.argv) != 3:
        print 'Command e.g.: python itemcf.py -tv 1.5'
        sys.exit(1)

    para = parser.parse_args()
    data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]
    user_bought = getUserBought(data)
    user_behavior = getUserBehavior(data)
    user_inverted_index = createdInvertedIndex(data)
    sim_items = itemSimilarity(user_inverted_index)
    #recommend_result = genRecommendResult(sim_items, user_bought, para.threshold_val)
    recommend_result = genRecommendResult1(sim_items, user_behavior, para.threshold_val)

    write_submission(recommend_result)

if __name__ == "__main__":
    main()
