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
sys.path.append("../")
from data_io import write_submission
#from model import BPR
#from model1 import BPR
from model2 import BPR

settings = json.loads(open("../../SETTINGS.json").read())


def genTrainFile(behavior_num):
    data = csv.reader(open(settings["TRAIN_DATA_FILE"]))
    skip_header_data = []
    for i, entry in enumerate(data):
        if i != 0:
            skip_header_data.append(entry)
    data = [map(int, feature) for feature in skip_header_data]

    train_data = []
    for entry in data:
        action_type = entry[2]
        uid = entry[0]
        pid = entry[1]
        if action_type == settings["ACTION_BUY"]:
            train_data.append([uid, pid, 1])
        if behavior_num == settings["BEHAVIOR_TRIPLE"] and action_type == settings["ACTION_CLICK"]:
            train_data.append([uid, pid, 0])
    writer = csv.writer(open(settings['BPR_TRAIN_FILE'], 'w'))
    writer.writerows(train_data)

def genTrainFile1(behavior_num):
    data = csv.reader(open(settings["TRAIN_DATA_FILE"]))
    skip_header_data = []
    for i, entry in enumerate(data):
        if i != 0:
            skip_header_data.append(entry)
    data = [map(int, feature) for feature in skip_header_data]

    train_data = []
    for entry in data:
        action_type = entry[2]
        uid = entry[0]
        pid = entry[1]
        if action_type == settings["ACTION_CLICK"]:
            train_data.append([uid, pid, 0])
    writer = csv.writer(open(settings['BPR_TRAIN_FILE'], 'w'))
    writer.writerows(train_data)


def genTrainFile2():
    data = [entry for entry in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [map(int, entry) for entry in data[1:]]
    train_data = []
    for entry in data:
        uid, pid, action_type = entry[0:3]
        if action_type == settings["ACTION_CLICK"]:
            train_data.append([uid, pid, 1])
        elif action_type == settings["ACTION_COLLECT"] or action_type == settings["ACTION_SHOPPING_CHART"]:
            train_data.append([uid, pid, 2])
        elif action_type == settings["ACTION_BUY"]:
            train_data.append([uid, pid, 3])
    writer = csv.writer(open(settings['BPR_TRAIN_FILE'], 'w'))
    writer.writerows(train_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-Csampling', type=str, action='store',
            dest='sample_method', help='specify which sampling method.\n'
            'Currently including three sampling method:\t1.uniform\n\t'
            '2.adaptive pairwise sampling')
    parser.add_argument('-Cbehavior', type=str, action='store',
            dest='behavior_num', help='specify whether to utilize various behaviours of users')
    parser.add_argument('-Init', type=str, action='store', dest='init_choice',
            help='specify which method to initialize model parameters')
    parser.add_argument('-Retrain', type=str, action='store',dest='retrain_choice',
            help='specify which method to initialize model parameters')
    parser.add_argument('-topk', type=int, action='store', dest='topk',
            help='specify how many products to be recommended')

    if len(sys.argv) != 11:
        print 'Command e.g.: python train.py -Retrain True -Init zero(gaussian) '\
                + '-Csampling uniform(adaptive) -Cbehavior triple(tuple) -topk 4'
        sys.exit(1)

    para = parser.parse_args()
    #genTrainFile(para.behavior_num)
    #genTrainFile1(para.behavior_num)
    genTrainFile2()
    #bpr = BPR()
    #bpr1 = BPR()
    bpr2 = BPR()
    if para.retrain_choice == "True":
        bpr2.model_init(settings["BPR_TRAIN_FILE"], para.init_choice)
        bpr2.train()
        recommend_result = bpr2.genRecommendResult(True, para.topk,
                settings["BPR_TRAIN_FILE"], para.init_choice)
        write_submission(recommend_result)
    else:
        recommend_result = bpr2.genRecommendResult(False, para.topk,
                settings["BPR_TRAIN_FILE"], para.init_choice)
        write_submission(recommend_result)

if __name__ == "__main__":
    main()
