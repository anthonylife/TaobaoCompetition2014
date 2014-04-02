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
from tool import getCFfeature, getUserBehavior, getLastDay, genDayUPfeature
from tool import genMonthUPfeature1, getProductPopularity, genProductFeature
from tool import getLastWeek, getLastHalfMonth, load_factor_model, getLastDate
from tool import genAnyDateIntervalUPfeature

settings = json.loads(open("../../SETTINGS.json").read())

MONTH_DAY_LENGTH = 30
CF_TV = 2.5

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=int, action='store',
            dest='file_num', help='choose to generate features for which file')

    if len(sys.argv) != 3:
        print 'Command e.g.: python makeFeature.py -d 0(1,2,3)'
        sys.exit(1)

    para = parser.parse_args()
    if para.file_num == 0:
        file_name = settings["GBT_TRAIN_PAIR_FOR_VALIDATION"]
        writer = csv.writer(open(settings["GBT_TRAIN_FILE"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE"])
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    elif para.file_num == 1:
        file_name = settings["GBT_TRAIN_PAIR_FOR_TEST"]
        writer = csv.writer(open(settings["GBT_TRAIN_FILE_FOR_SUBMIT"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE_FOR_SUBMIT"])
        data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    elif para.file_num == 2:
        file_name = settings["GBT_TEST_PAIR_FOR_VALIDATION"]
        writer = csv.writer(open(settings["GBT_TEST_FILE"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE"])
        data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    elif para.file_num == 3:
        file_name = settings["GBT_TEST_PAIR_FOR_TEST"]
        writer = csv.writer(open(settings["GBT_TEST_FILE_FOR_SUBMIT"], "w"), lineterminator="\n")
        cf_feature = getCFfeature(settings["CF_FEATURE_FILE_FOR_SUBMIT"])
        data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
        data = [map(int, entry) for entry in data[1:]]
    else:
        print 'Choice of file invalid!'
        sys.exit(1)

    # Feature: (uid, pid)+(cf score)+(last day feature: action*2)
    feature_num = 2 + 3*2 + 3*2 + 3*2
    #feature_num = 1+3*2
    #feature_num = 2+1+3*2
    user_behavior = getUserBehavior(data)
    product_popularity = getProductPopularity(data)
    user_factor = load_factor_model((settings["WMF_MODEL_USER_FILE"]))
    product_factor = load_factor_model((settings["WMF_MODEL_PRODUCT_FILE"]))
    for i, pair in enumerate(csv.reader(open(file_name))):
        feature_idx = 2
        if para.file_num == 0 or para.file_num == 1:
            output_feature = [0 for ii in xrange(feature_num+3)]
            uid,pid,month,day,target = map(int, pair)
            output_feature[:2] = [uid, pid]
            output_feature[-1] = target
        else:
            output_feature = [0 for ii in xrange(feature_num+2)]
            uid,pid,month,day = map(int, pair)
            output_feature[:2] = [uid, pid]

        # 1.user and item id
        #output_feature[feature_idx] = uid
        #feature_idx += 1
        #output_feature[feature_idx] = pid
        #feature_idx += 1

        # 2.adding cf feature
        if uid in cf_feature:
            if pid in cf_feature[uid]:
                if cf_feature[uid][pid] > CF_TV:
                    output_feature[feature_idx] = 1
                else:
                    output_feature[feature_idx] = 0
                output_feature[feature_idx+1] = 0
            else:
                output_feature[feature_idx] = -1
                output_feature[feature_idx+1] = 1
        else:
            output_feature[feature_idx] = -1
            output_feature[feature_idx+1] = 1
        feature_idx += 2
        '''if uid in user_factor and pid in product_factor:
            output_feature[feature_idx] = np.dot(user_factor[uid],
                    product_factor[pid])
        else:
            output_feature[feature_idx] = -1
        feature_idx += 1'''

        # 3.adding last day interaction feature
        if para.file_num == 2:
            last_month = settings["VALIDATION_TIME_LAST_MONTH"]
            last_day = settings["VALIDATION_TIME_LAST_DAY"]
        elif para.file_num == 3:
            last_month = settings["TIME_LAST_MONTH"]
            last_day = settings["TIME_LAST_DAY"]
        else:
            last_month, last_day = getLastDay(month, day)
        output_feature[feature_idx:feature_idx+2*3] = genDayUPfeature(user_behavior[uid], pid, last_month, last_day)
        feature_idx += 2*3

        # 4.adding last week interaction feature
        if para.file_num == 2:
            last_month, last_day = getLastWeek(settings["VALIDATION_TIME_LAST_MONTH"], settings["VALIDATION_TIME_LAST_DAY"])
        elif para.file_num == 3:
            last_month, last_day = getLastWeek(settings["TIME_LAST_MONTH"], settings["TIME_LAST_DAY"])
        else:
            last_month, last_day = getLastWeek(month, day)
        output_feature[feature_idx:feature_idx+2*3] = genMonthUPfeature1(user_behavior[uid], pid, month, day, last_month, last_day)
        feature_idx += 2*3

        # 5.adding half month interaction feature
        '''if para.file_num == 2:
            last_month, last_day = getLastHalfMonth(settings["VALIDATION_TIME_LAST_MONTH"], settings["VALIDATION_TIME_LAST_DAY"])
        elif para.file_num == 3:
            last_month, last_day = getLastHalfMonth(settings["TIME_LAST_MONTH"], settings["TIME_LAST_DAY"])
        else:
            last_month, last_day = getLastHalfMonth(month, day)
        output_feature[feature_idx:feature_idx+2*3] = genMonthUPfeature1(user_behavior[uid], pid, month, day, last_month, last_day)
        feature_idx += 2*3'''

        # 6.adding last month interaction feature
        if para.file_num == 2:
            last_month = settings["VALIDATION_TIME_LAST_MONTH"]-1
            last_day = settings["VALIDATION_TIME_LAST_DAY"]
        elif para.file_num == 3:
            last_month = settings["TIME_LAST_MONTH"]-1
            last_day = settings["TIME_LAST_DAY"]-1
        else:
            last_month = month-1
            last_day = day
        #output_feature[feature_idx:feature_idx+3] = genMonthUPfeature1(user_behavior[uid],
        #            pid, month, day, last_month, last_day)
        #feature_idx += 3
        output_feature[feature_idx:feature_idx+2*3] = genMonthUPfeature1(user_behavior[uid],
                    pid, month, day, last_month, last_day)
        feature_idx += 2*3

        # 7.adding every day interaction feature in last month
        '''if para.file_num == 2:
            last_month, last_day = getLastDate(settings["VALIDATION_TIME_LAST_MONTH"], settings["VALIDATION_TIME_LAST_DAY"], MONTH_DAY_LENGTH)
        elif para.file_num == 3:
            last_month, last_day = getLastDate(settings["TIME_LAST_MONTH"], settings["TIME_LAST_DAY"], MONTH_DAY_LENGTH)
        else:
            last_month, last_day = getLastDate(month, day, MONTH_DAY_LENGTH)
        output_feature[feature_idx:feature_idx+3*MONTH_DAY_LENGTH] = genAnyDateIntervalUPfeature(user_behavior[uid], pid, month, day, last_month, last_day, MONTH_DAY_LENGTH)
        feature_idx += 3*MONTH_DAY_LENGTH'''

        # 7.adding product last day popularity feature
        '''if para.file_num == 2:
            last_month = settings["VALIDATION_TIME_LAST_MONTH"]
            last_day = settings["VALIDATION_TIME_LAST_DAY"]
        elif para.file_num == 3:
            last_month = settings["TIME_LAST_MONTH"]
            last_day = settings["TIME_LAST_DAY"]
        else:
            last_month, last_day = getLastDay(month, day)
        output_feature[feature_idx:feature_idx+3] = genProductFeature(product_popularity[pid], month, day, last_month, last_day)
        feature_idx += 3'''

        # 8.adding product last week popularity feature
        '''if para.file_num == 2:
            last_month, last_day = getLastWeek(settings["VALIDATION_TIME_LAST_MONTH"], settings["VALIDATION_TIME_LAST_DAY"]+1)
        elif para.file_num == 3:
            last_month, last_day = getLastWeek(settings["VALIDATION_TIME_LAST_MONTH"], settings["VALIDATION_TIME_LAST_DAY"]+1)
        else:
            last_month, last_day = getLastWeek(month, day)
        output_feature[feature_idx:feature_idx+3] = genProductFeature(product_popularity[pid], month, day, last_month, last_day)
        feature_idx += 3'''

        # 9.adding product last month popularity feature
        '''if para.file_num == 2:
            last_month = settings["VALIDATION_TIME_LAST_MONTH"]-1
            last_day = settings["VALIDATION_TIME_LAST_DAY"]
        elif para.file_num == 3:
            last_month = settings["TIME_LAST_MONTH"]-1
            last_day = settings["TIME_LAST_DAY"]-1
        else:
            last_month = month-1
            last_day = day
        output_feature[feature_idx:feature_idx+3] = genProductFeature(product_popularity[pid], month, day, last_month, last_day)
        feature_idx += 3'''

        if (i%1000) == 0 and i != 0:
            sys.stdout.write("\rFINISHED PAIR NUM: %d. " % (i+1))
            sys.stdout.flush()
        writer.writerow(output_feature)


if __name__ == "__main__":
    main()

