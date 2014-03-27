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
# Date: 2014/3/24                                                 #
# Generate recommendation results based on GBT                    #
###################################################################

import sys, csv, json, argparse
sys.path.append("../")
import data_io
from collections import defaultdict
from tool import calSegNum

settings = json.loads(open("../../SETTINGS.json").read())


def getProductSellNum():
    data = [entry for entry in csv.reader(open(settings["TAR_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]

    product_selluser = {}
    for entry in data:
        uid = entry[0]
        pid = entry[1]
        action_type = entry[2]
        month = entry[3]
        day = entry[4]
        if action_type == 1:
            seg_num = calSegNum(month, day)
            if pid not in product_selluser:
                product_selluser[pid] = [set(), set(), set()]
            product_selluser[pid][seg_num-1].add(uid)
    product_sellnum = {}
    for pid in product_selluser:
        total_num = 0
        for i in xrange(3):
            total_num += len(product_selluser[pid][i])
        product_sellnum[pid] = total_num/3+1
    return product_sellnum


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-mPred', type=int, action='store',
            dest='rec_num', help='specify how to generate recommendation result.')
    if len(sys.argv) != 3:
        print 'Command e.g.: python predict.py -mPred(0 or >0)'
        sys.exit(1)

    classifier = data_io.load_model()

    user_recommend_result = defaultdict(list)
    para = parser.parse_args()
    if para.rec_num > 0:
        features = []
        user_product_ids = []
        cache_uid = -1
        finished_num = 0
        for i, entry in enumerate(csv.reader(open(settings["GBT_TEST_FILE_FOR_SUBMIT"]))):
            pair = map(float, entry[:2])
            uid, pid = map(int, pair)
            if i == 0:
                cache_uid = uid
            if uid != cache_uid:
                predictions = classifier.predict_proba(features)[:,1]
                predictions = list(predictions)
                user_predictions = []
                for (t_uid, t_pid), pred in zip(user_product_ids, predictions):
                    user_predictions.append((pred, t_pid))
                sorted_result = sorted(user_predictions, reverse=True)
                pid_sorted = [x[1] for x in sorted_result]
                user_recommend_result[cache_uid] = pid_sorted[:para.rec_num]
                features = [map(float, entry[2:])]
                user_product_ids = [[uid, pid]]
                cache_uid = uid
                finished_num += 1
                print finished_num
            else:
                features.append(map(float, entry[2:]))
                user_product_ids.append([uid, pid])

    else:
        product_sellnum = getProductSellNum()
        product_predictions = defaultdict(list)
        features = []
        user_product_ids = []
        cache_uid = -1
        finished_num = 0
        for i, entry in enumerate(csv.reader(open(settings["GBT_TEST_FILE_FOR_SUBMIT"]))):
            pair = map(float, entry[:2])
            uid, pid = map(int, pair)
            if i == 0:
                cache_uid = uid
            if uid != cache_uid:
                predictions = classifier.predict_proba(features)[:,1]
                predictions = list(predictions)
                for (t_uid, t_pid), pred in zip(user_product_ids, predictions):
                    product_predictions[t_pid].append((pred, t_uid))
                features = [map(float, entry[2:])]
                user_product_ids = [[uid, pid]]
                cache_uid = uid
                finished_num += 1
                print finished_num
            else:
                features.append(map(float, entry[2:]))
                user_product_ids.append([uid, pid])

        recommend_pairs = []
        for pid in product_predictions:
            if pid not in product_sellnum:
                continue
            sorted_results = sorted(product_predictions[pid], reverse=True)
            uid_sorted = [x[1] for x in sorted_results]
            for uid in uid_sorted[:product_sellnum[pid]]:
                recommend_pairs.append([uid, pid])
        for pair in recommend_pairs:
            user_recommend_result[pair[0]].append(pair[1])

    data_io.write_submission(user_recommend_result)


if __name__ == "__main__":
    main()
