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
# Time-aware based Item-based CF method                           #
#   including time penalty, multiple behavior
###################################################################

import sys, csv, json, argparse, math
sys.path.append("../")
from collections import defaultdict
from data_io import write_submission
from tool import getDayDiff, getUserBehavior

settings = json.loads(open("../../SETTINGS.json").read())

TOP_SIM_NUM = 10
TOPK = 5
BELIEF_CNT = 4


def createdInvertedIndex(data):
    ''' Without considering the difference between different actions '''
    user_inverted_index = {}
    for entry in data:
        uid, pid, action_type, month, day = entry
        if uid not in user_inverted_index:
            user_inverted_index[uid] = [[], [], []]
        if action_type == 1:
            user_inverted_index[uid][0].append([pid, month, day])
        elif action_type == 2 or action_type == 3:
            user_inverted_index[uid][1].append([pid, month, day])
        elif action_type == 0:
            user_inverted_index[uid][2].append([pid, month, day])
    return user_inverted_index

def createdInvertedIndex1(data):
    user_inverted_index = {}


def itemSimilarity(user_inverted_index, click_score, collect_score,
        buy_score, time_alpha):
    ''' considering buy behaviors to compute similarity with no count info '''
    count_matrix = {}
    item_count = defaultdict(list)
    #behavior_score = [buy_score/buy_score, 1.0*collect_score/buy_score,
    #        1.0*click_score/buy_score]
    behavior_score = [1.0, 1.0, 1.0]
    for uid in user_inverted_index:
        for entry1 in user_inverted_index[uid][0]:
            pid1, month1, day1 = entry1
            item_count[pid1].append(uid)
            for entry2 in user_inverted_index[uid][0]:
                pid2, month2, day2 = entry2
                if pid1 == pid2:
                    continue
                time_penality = 1.0/(1+time_alpha*
                        abs(getDayDiff(month1, day1, month2, day2)))
                if pid1 not in count_matrix:
                    count_matrix[pid1] = {}
                if pid2 not in count_matrix[pid1]:
                    count_matrix[pid1][pid2] = behavior_score[0]*time_penality
                else:
                    count_matrix[pid1][pid2] += behavior_score[0]*time_penality

    sim_matrix = defaultdict(dict)
    for pid1 in count_matrix:
        for pid2 in count_matrix[pid1]:
            if pid1 == pid2:
                sim_matrix[pid1][pid2] = 1
            else:
                sim_matrix[pid1][pid2] = count_matrix[pid1][pid2]\
                    /math.sqrt(len(item_count[pid1])*len(item_count[pid2]))
                print pid1, pid2
                print count_matrix[pid1][pid2], len(item_count[pid1]), len(item_count[pid2])
                raw_input()

    sim_items = {}
    for pid in sim_matrix:
        #sim_sum = sum([entry[1] for entry in sim_matrix[pid].items()])
        tmp_items = sorted(sim_matrix[pid].items(), key=lambda x:x[1], reverse=True)
        #sim_items[pid] = [[entry[0], entry[1]/sim_sum] for entry in tmp_items[:TOP_SIM_NUM]]
        sim_items[pid] = tmp_items[:TOP_SIM_NUM]
        print pid, sim_items[pid]
        raw_input()
    return sim_items


def itemSimilarity1(user_inverted_index, click_score, collect_score,
        buy_score, time_alpha):
    ''' considering buy behaviors to compute similarity with count info '''
    count_matrix = {}
    item_count = defaultdict(set)
    #behavior_score = [buy_score/buy_score, 1.0*collect_score/buy_score,
    #        1.0*click_score/buy_score]
    behavior_score = [1.0, 1.0, 1.0]
    for ii, uid in enumerate(user_inverted_index):
        tmp_count_matrix = {}
        tmp_item_count = {}
        #print '%d...\n' % (ii+1) ,
        for entry1 in user_inverted_index[uid][0]:
            pid1, month1, day1 = entry1
            item_count[pid1].add(uid)
            if pid1 not in tmp_item_count:
                tmp_item_count[pid1] = 1
            else:
                tmp_item_count[pid1] += 1
            for entry2 in user_inverted_index[uid][0]:
                pid2, month2, day2 = entry2
                if pid1 == pid2:
                    continue
                time_penality = 1.0/(1+time_alpha*
                        abs(getDayDiff(month1, day1, month2, day2)))
                if pid1 not in tmp_count_matrix:
                    tmp_count_matrix[pid1] = {}
                if pid2 not in tmp_count_matrix[pid1]:
                    tmp_count_matrix[pid1][pid2] = behavior_score[0]*time_penality
                else:
                    tmp_count_matrix[pid1][pid2] += behavior_score[0]*time_penality
        for pid1 in tmp_count_matrix:
            if pid1 not in count_matrix:
                count_matrix[pid1] = {}
            for pid2 in tmp_count_matrix[pid1]:
                if pid2 not in count_matrix[pid1]:
                    count_matrix[pid1][pid2] = tmp_count_matrix[pid1][pid2]/(tmp_item_count[pid1]*tmp_item_count[pid2])
                else:
                    count_matrix[pid1][pid2] += tmp_count_matrix[pid1][pid2]/(tmp_item_count[pid1]*tmp_item_count[pid2])

    sim_matrix = defaultdict(dict)
    for pid1 in count_matrix:
        sim_matrix[pid1][pid1] = 1
        for pid2 in count_matrix[pid1]:
            if pid1 == pid2:
                continue
            else:
                if len(item_count[pid1]) < BELIEF_CNT or len(item_count[pid2]) < BELIEF_CNT:
                    sim_matrix[pid1][pid2] = 0.0
                else:
                    sim_matrix[pid1][pid2] = count_matrix[pid1][pid2]\
                        /(math.sqrt(len(item_count[pid1])*len(item_count[pid2])))
                #print pid1, pid2
                #print count_matrix[pid1][pid2], len(item_count[pid1]), len(item_count[pid2])
                #raw_input()

    sim_items = {}
    for pid in sim_matrix:
        sim_sum = sum([entry[1] for entry in sim_matrix[pid].items()])
        tmp_items = sorted(sim_matrix[pid].items(), key=lambda x:x[1], reverse=True)
        #sim_items[pid] = [[entry[0], entry[1]/sim_sum] for entry in tmp_items[:TOP_SIM_NUM]]
        sim_items[pid] = tmp_items[:TOP_SIM_NUM]
        #print pid, sim_items[pid]
        #raw_input()
    return sim_items


def itemSimilarity2(user_inverted_index, click_score, collect_score,
        buy_score, time_alpha):
    ''' considering multiple behaviors to compute similarity  '''
    count_matrix = {}
    item_count = defaultdict(list)
    #behavior_score = [buy_score/buy_score, 1.0*collect_score/buy_score,
    #        1.0*click_score/buy_score]
    behavior_score = [1.0, 1.0, 1.0]
    for uid in user_inverted_index:
        for entry1 in user_inverted_index[uid][0]:
            pid1, month1, day1 = entry1
            item_count[pid1].append(uid)
            for entry2 in user_inverted_index[uid][0]:
                pid2, month2, day2 = entry2
                if pid1 == pid2:
                    continue
                time_penality = 1.0/(1+time_alpha*
                        abs(getDayDiff(month1, day1, month2, day2)))
                if pid1 not in count_matrix:
                    count_matrix[pid1] = {}
                if pid2 not in count_matrix[pid1]:
                    count_matrix[pid1][pid2] = behavior_score[0]*time_penality
                else:
                    count_matrix[pid1][pid2] += behavior_score[0]*time_penality
                if pid2 not in count_matrix:
                    count_matrix[pid2] = {}
                if pid1 not in count_matrix[pid2]:
                    count_matrix[pid2][pid1] = behavior_score[0]*time_penality
                else:
                    count_matrix[pid2][pid1] += behavior_score[0]*time_penality

    count_matrix2 = {}
    item_count2 = defaultdict(list)
    for uid in user_inverted_index:
        for entry1 in user_inverted_index[uid][2]:
            pid1, month1, day1 = entry1
            item_count2[pid1].append(uid)
            for entry2 in user_inverted_index[uid][2]:
                pid2, month2, day2 = entry2
                if pid1 == pid2:
                    continue
                time_penality = 1.0/(1+time_alpha*
                        abs(getDayDiff(month1, day1, month2, day2)))
                if pid1 not in count_matrix2:
                    count_matrix2[pid1] = {}
                if pid2 not in count_matrix2[pid1]:
                    count_matrix2[pid1][pid2] = behavior_score[2]*time_penality
                else:
                    count_matrix2[pid1][pid2] += behavior_score[2]*time_penality
                if pid2 not in count_matrix2:
                    count_matrix2[pid2] = {}
                if pid1 not in count_matrix2[pid2]:
                    count_matrix2[pid2][pid1] = behavior_score[2]*time_penality
                else:
                    count_matrix2[pid2][pid1] += behavior_score[2]*time_penality

    sim_matrix = defaultdict(dict)
    for pid1 in count_matrix:
        for pid2 in count_matrix[pid1]:
            if pid1 == pid2:
                sim_matrix[pid1][pid2] = 1
            else:
                val1 = count_matrix[pid1][pid2]/math.sqrt(len(item_count[pid1])*len(item_count[pid2]))
                val2 = count_matrix2[pid1][pid2]/math.sqrt(len(item_count2[pid1])*len(item_count2[pid2]))
                sim_matrix[pid1][pid2] = (buy_score*val1 + click_score*val2)/(val1+val2)

    sim_items = {}
    for pid in sim_matrix:
        #sim_sum = sum([entry[1] for entry in sim_matrix[pid].items()])
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

    return recommend_result


def genRecommendResult1(sim_items, user_behavior, click_score, collect_score,
        buy_score, time_beta, t_val, re_month, re_day, target):
    user_result = defaultdict(dict)
    for uid in user_behavior:
        for entry in user_behavior[uid][0]:
            pid, src_month, src_day = entry
            time_penality = 1.0/(1+time_beta*
                    abs(getDayDiff(src_month, src_day, re_month, re_day)))
            if pid not in sim_items:
                continue
            for entry in sim_items[pid]:
                pid1, sim_score = entry
                if pid1 not in user_result[uid]:
                    user_result[uid][pid1] = 0.0
                user_result[uid][pid1] += sim_score*buy_score*time_penality
        for entry in user_behavior[uid][1]:
            pid, src_month, src_day = entry
            time_penality = 1.0/(1+time_beta*
                    abs(getDayDiff(src_month, src_day, re_month, re_day)))
            if pid not in sim_items:
                continue
            for entry in sim_items[pid]:
                pid1, sim_score = entry
                if pid1 not in user_result[uid]:
                    user_result[uid][pid1] = 0.0
                user_result[uid][pid1] += sim_score*collect_score*time_penality
        for entry in user_behavior[uid][2]:
            pid, src_month, src_day = entry
            time_penality = 1.0/(1+time_beta*
                    abs(getDayDiff(src_month, src_day, re_month, re_day)))
            if pid not in sim_items:
                continue
            for entry in sim_items[pid]:
                pid1, sim_score = entry
                if pid1 not in user_result[uid]:
                    user_result[uid][pid1] = 0.0
                user_result[uid][pid1] += sim_score*click_score*time_penality

    if target == 0:
        writer = csv.writer(open(settings["CF_FEATURE_FILE"], "w"), lineterminator="\n")
    elif target == 1:
        writer = csv.writer(open(settings["CF_FEATURE_FILE_FOR_SUBMIT"], "w"), lineterminator="\n")
    else:
        print 'Invalid train data target choice...'
        sys.exit(1)
    recommend_result = defaultdict(list)
    for uid in user_result:
        for entry in user_result[uid].items():
            pid, score = entry
            writer.writerow([uid, pid, score])
            if score > t_val:
                recommend_result[uid].append(pid)
                #writer.writerow([uid, pid, 1])

    return recommend_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=int, action='store',
            dest='target', help='for validation or test dataset')
    parser.add_argument('-tv', type=float, action='store', dest='threshold_val',
            help='specify threshold value.')
    parser.add_argument('-s1', type=float, action='store', dest='click_score',
            help='specify the score of user click behavior.')
    parser.add_argument('-s2', type=float, action='store', dest='collect_score',
            help='specify the score of user click behavior.')
    parser.add_argument('-s3', type=float, action='store', dest='buy_score',
            help='specify the score of user click behavior.')
    parser.add_argument('-ta', type=float, action='store', dest='time_alpha',
            help='specify the decay parameter for training')
    parser.add_argument('-tb', type=float, action='store', dest='time_beta',
            help='specify the decay parameter for prediction')
    parser.add_argument('-month', type=int, action='store', dest='month',
            help='specify the month when the recommendation being generated.')
    parser.add_argument('-day', type=int, action='store', dest='day',
            help='specify the day when the recommendation being generated.')

    if len(sys.argv) != 19:
        print 'Command e.g.: python itemcf.py -t (1) -tv 1.5 -s1 1 -s2 2 -s3 4 -ta 0.5 -tb 0.5 -month 7 -day 15'
        sys.exit(1)

    para = parser.parse_args()
    if para.target == 0:
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    elif para.target == 1:
        data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
    else:
        print 'Invalid train data target choice...'
        sys.exit(1)
    data = [map(int, entry) for entry in data[1:]]
    user_behavior = getUserBehavior(data)
    user_inverted_index = createdInvertedIndex(data)
    #user_inverted_index = createdInvertedIndex1(data)
    #sim_items = itemSimilarity(user_inverted_index, para.click_score,
    #        para.collect_score, para.buy_score, para.time_alpha)
    sim_items = itemSimilarity1(user_inverted_index, para.click_score,
            para.collect_score, para.buy_score, para.time_alpha)
    #recommend_result = genRecommendResult(sim_items, user_behavior, para.click_score,
    #        para.collect_score, para.buy_score, para.time_alpha, para.threshold_val,
    #        para.month, para.day)
    recommend_result = genRecommendResult1(sim_items, user_behavior, para.click_score,
            para.collect_score, para.buy_score, para.time_beta, para.threshold_val,
            para.month, para.day, para.target)

    write_submission(recommend_result)

if __name__ == "__main__":
    main()
