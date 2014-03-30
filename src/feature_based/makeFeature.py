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
settings = json.loads(open("../../SETTINGS.json").read())


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
    elif para.file_num == 1:
        file_name = settings["GBT_TRAIN_PAIR_FOR_TEST"]
        writer = csv.writer(open(settings["GBT_TRAIN_FILE_FOR_SUBMIT"], "w"), lineterminator="\n")
    elif para.file_num == 2:
        file_name = settings["GBT_TEST_PAIR_FOR_VALIDATION"]
        writer = csv.writer(open(settings["GBT_TEST_FILE"], "w"), lineterminator="\n")
    elif para.file_num == 3:
        file_name = settings["GBT_TEST_PAIR_FOR_TEST"]
        writer = csv.writer(open(settings["GBT_TEST_FILE_FOR_SUBMIT"], "w"), lineterminator="\n")
    else:
        print 'Choice of file invalid!'
        sys.exit(1)

    feature_num = 2
    for pair in csv.reader(open(file_name)):
        feature_idx = 0
        if para.file_num == 0 or para.file_name == 1:
            output_feature = [0 for i in xrange(feature_num+1)]
            uid,pid,month,day,target = map(int, pair)
            output_feature[-1] = target
        else:
            output_feature = [0 for i in xrange(feature_num)]
            uid,pid,month,day = map(int, pair)

        # user and item id
        output_feature[feature_idx] = uid
        feature_idx += 1
        output_feature[feature_idx] = pid
        feature_idx += 2


        writer.writerow(output_feature)

if __name__ == "__main__":
    main()

