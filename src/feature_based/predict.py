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
# Date: 2014/4/1                                                  #
# Generate recommendation results based on GBT                    #
###################################################################

import sys, csv, json, argparse
sys.path.append("../")
import data_io
from collections import defaultdict
from tool import calSegNum

settings = json.loads(open("../../SETTINGS.json").read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tv', type=float, action='store',
            dest='threshold_val', help='specify how to generate recommendation result.')
    parser.add_argument('-t', type=int, action='store',
            dest='target', help='for validation or test dataset')

    if len(sys.argv) != 5:
        print 'Command e.g.: python predict.py -tv 0.8 -t 0(1)'
        sys.exit(1)

    para = parser.parse_args()
    if para.target == 0:
        file_name = settings["GBT_TEST_FILE"]
    elif para.target == 1:
        file_name = settings["GBT_TEST_FILE_FOR_SUBMIT"]

    classifier = data_io.load_model(settings["GBT_MODEL_FILE"])
    user_recommend_result = defaultdict(list)
    finished_num = 0
    features = []
    user_product_ids = []
    cache_uid = -1
    for i, entry in enumerate(csv.reader(open(file_name))):
        feature = map(float, entry[2:])
        uid, pid = map(int, entry[:2])
        if i == 0:
            cache_uid = uid
        if uid != cache_uid:
            predictions = classifier.predict_proba(features)[:,1]
            #predictions = classifier.predict(features)
            predictions = list(predictions)
            for (t_uid, t_pid), pred in zip(user_product_ids, predictions):
                if pred > para.threshold_val:
                    user_recommend_result[t_uid].append(t_pid)
            features = [feature]
            user_product_ids = [[uid, pid]]
            cache_uid = uid
            finished_num += 1
            #print("FINISHED UID NUM: %d. " % (finished_num))
            #sys.stderr.write("\rFINISHED UID NUM: %d. " % (finished_num))
            #sys.stderr.flush()
        else:
            features.append(feature)
            user_product_ids.append([uid, pid])

    data_io.write_submission(user_recommend_result)


if __name__ == "__main__":
    main()


