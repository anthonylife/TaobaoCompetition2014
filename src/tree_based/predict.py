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

settings = json.loads(open("../../SETTINGS.json").read())


def getProductSellNum():


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-mPred', type=int, action='store',
            dest='rec_num', help='specify how to generate recommendation result.')
    if len(sys.argv) != 3:
        print 'Command e.g.: python predict.py -mPred(0 or >0)'
        sys.exit(1)

    data = csv.reader(open(settings["GBT_TEST_FILE"]))
    user_product_ids = [map(int, entry[:2]) for entry in data]
    features = [map(float, entry[2:]) for entry in data]

    classifier = data_io.load_model()
    predictions = classifier.predict_proba(features)[:,1]
    predictions = list(predictions)

    user_recommend_result = {}
    para = parser.parse_args()
    if para.rec_num > 0:
        user_predictions = defaultdict(list)
        for (uid, pid), pred in zip(user_product_ids, predictions):
            user_predictions[uid].append((pred, pid))
        for uid in sorted(user_predictions):
            sorted_result = sorted(user_predictions[uid], reverse=True)
            pid_sorted = [x[1] for x in sorted_result]
            user_recommend_result[uid] = pid_sorted[para.rec_num]
    else:


    data_io.write_submission(user_recommend_result)


if __name__ == "__main__":
    main()
