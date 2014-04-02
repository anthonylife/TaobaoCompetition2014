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
# Date: 2014/3/28                                                 #
# Make feature for decision/regression method                     #
# Feature lists: 1.user and item id                               #
###################################################################

import sys, csv, json, argparse, random
sys.path.append("../")
import numpy as np
from collections import defaultdict
from tool import getCFfeature, getUserBehavior, genDayUPfeature
from tool import getLastDayBySegnum, genMonthUPfeature, underSampling
from tool import getProductPopularity, genProductFeature, getLastWeekBySegnum
from tool import genMonthUPfeature1

settings = json.loads(open("../../SETTINGS.json").read())

MONTH_DAY = [[4,15], [5,15], [6,15], [7,15], [8,16]]
RATIO = 2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=int, action='store',
            dest='file_num', help='choose to generate features for which file')

    if len(sys.argv) != 3:
        print 'Command e.g.: python makeFeature.py -d 0(1,2,3)'
        sys.exit(1)

    para = parser.parse_args()
    if para.file_num == 0:
        file_name = settings["LR_TRAIN_PAIR_FOR_VALIDATION"]
        writer = csv.writer(open(settings["LR_TRAIN_FILE"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE"])
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    elif para.file_num == 1:
        file_name = settings["LR_TRAIN_PAIR_FOR_TEST"]
        writer = csv.writer(open(settings["LR_TRAIN_FILE_FOR_SUBMIT"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE_FOR_SUBMIT"])
        data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    elif para.file_num == 2:
        file_name = settings["LR_TEST_PAIR_FOR_VALIDATION"]
        writer = csv.writer(open(settings["LR_TEST_FILE"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE"])
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    elif para.file_num == 3:
        file_name = settings["LR_TEST_PAIR_FOR_TEST"]
        writer = csv.writer(open(settings["LR_TEST_FILE_FOR_SUBMIT"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE_FOR_SUBMIT"])
        data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    else:
        print 'Choice of file invalid!'
        sys.exit(1)

    # Feature: (uid, pid)+(cf score)+(last day feature: action*2)
    #feature_num = 2
    #feature_num = 2+1
    #feature_num = 2+1+3*2
    feature_num = 3*2 + 3*2 + 3*2
    user_behavior = getUserBehavior(data)
    product_popularity = getProductPopularity(data)
    output_features = []
    for i, pair in enumerate(csv.reader(open(file_name))):
        feature_idx = 2
        if para.file_num == 0 or para.file_num == 1:
            output_feature = [0 for ii in xrange(feature_num+3)]
            uid,pid,seg_num,target = map(int, pair)
            output_feature[:2] = [uid, pid]
            output_feature[-1] = target
        else:
            output_feature = [0 for ii in xrange(feature_num+2)]
            uid,pid,seg_num = map(int, pair)
            output_feature[:2] = [uid, pid]

        # 1.user and item id
        #output_feature[feature_idx] = uid
        #feature_idx += 1
        #output_feature[feature_idx] = pid
        #feature_idx += 1

        # 2.adding cf feature
        '''if uid in cf_feature:
            if pid in cf_feature[uid]:
                output_feature[feature_idx] = cf_feature[uid][pid]
            else:
                output_feature[feature_idx] = 0.0
        else:
            output_feature[feature_idx] = 0.0
        feature_idx += 1'''

        # 3.adding last day feature of user product interaction
        last_month, last_day = getLastDayBySegnum(seg_num)
        output_feature[feature_idx:feature_idx+2*3] = genDayUPfeature(user_behavior[uid], pid, last_month, last_day)
        feature_idx += 2*3

        # 4.adding last week feature of user product interaction
        last_month, last_day = getLastWeekBySegnum(seg_num)
        output_feature[feature_idx:feature_idx+2*3] = genMonthUPfeature1(user_behavior[uid], pid, MONTH_DAY[seg_num-1][0], MONTH_DAY[seg_num-1][1], last_month, last_day)
        feature_idx += 2*3

        # 5.adding last month feature of user product interaction
        output_feature[feature_idx:feature_idx+2*3] = genMonthUPfeature(user_behavior[uid], pid, seg_num-1)
        feature_idx += 2*3

        # 6.adding product last day popularity feature
        '''last_month, last_day = getLastDayBySegnum(seg_num)
        output_feature[feature_idx:feature_idx+3] = genProductFeature(product_popularity[pid], MONTH_DAY[seg_num-1][0],
                MONTH_DAY[seg_num-1][1], last_month, last_day)
        feature_idx += 3'''


        if (i%1000) == 0 and i != 0:
            sys.stdout.write("\rFINISHED PAIR NUM: %d. " % (i+1))
            sys.stdout.flush()

        if para.file_num == 0 or para.file_num == 1:
            output_features.append(output_feature)
        else:
            writer.writerow(output_feature)

    if para.file_num == 0 or para.file_num == 1:
        output_features = underSampling(output_features, RATIO)
        writer.writerows(output_features)


if __name__ == "__main__":
    main()

