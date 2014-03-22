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
# Date: 2014/3/18                                                 #
# Call model.py to do airwise learning                            #
###################################################################

import sys, csv, json, argparse
from collections import defaultdict
from data_io import write_submission
from tool import getAverageUserBuy

settings = json.loads(open("../../SETTINGS.json").read())


def genTrainFile(behavior_choice):
    data = csv.reader(open(settings["TRAIN_DATA_FILE"]))
    data = [map(int, feature) for feature in data[1:]]

    train_data = []
    for entry in data:
        action_type = entry[2]
        uid = entry[0]
        pid = entry[1]
        if action_type == settings["ACTION_BUY"]:
            train_data.append([uid, pid, 1])
        if behavior_choice == 'various' and action_type == settings["ACTION_CLICK"]:
            train_data.append([uid, pid, 0])
    writer = csv.writer(open(settings['BPR_TRAIN_FILE', 'w']))
    writer.writerows(train_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-Csampling', type=str, action='store',
            dest='samling_choice', help='specify which sampling method.\n'
            'Currently including three sampling method:\t1.uniform\n\t'
            '2.adaptive pairwise sampling\n\t3.adaptive listwise sampling')
    parser.add_argument('-Cbehavior', type=str, action='store',
            dest='behavior_choice', help='specify whether to utilize various behaviours of users')
    parser.add_argument('-Init', type=str, action='store', dest='init_choice',
            help='specify which method to initialize model parameters')
    parser.

    if len(sys.argv) != 9:
        print 'Command e.g.: python train.py -Init zero(gaussian) '\
                + '-Csampling uniform(pairwise/listwise) -Cbehavior single(various)'
        sys.exit(1)

    para = parser.parse_args()
    genTrainFile(para.behavior_choice)


if __name__ == "__main__":
    main()
