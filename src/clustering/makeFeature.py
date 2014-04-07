#!/usr/bin/env python
#encoding=utf8

#Copyright [2014] [Wei Zhang]
#Licensed under the Apache License, Version 2.0 (the "License"); #you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

###################################################################
# Date: 2014/4/4                                                  #
# Generate feature for each user and product                      #
###################################################################
import csv, json, sys, argparse
sys.path.append("../")
from tool import getAttrDict

settings = json.loads(open("../../SETTINGS.json").read())
ACTION_WEIGHT = [1, 4, 2, 2]

def genUserFeatures(data, pid_dict):
    features = {}
    for entry in data:
        uid, pid, action = entry[:3]
        if uid not in features:
            features[uid] = [0 for i in xrange(len(pid_dict))]
        #features[uid][pid_dict[pid]] += ACTION_WEIGHT[action]
        features[uid][pid_dict[pid]] = 1
    return features


def genItemFeatures(data, uid_dict):
    features = {}
    for entry in data:
        uid, pid, action = entry[:3]
        if pid not in features:
            features[pid] = [0 for i in xrange(len(uid_dict))]
        #features[pid][uid_dict[uid]] += ACTION_WEIGHT[action]
        features[pid][uid_dict[uid]] = 1
    return features


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=int, action='store',
            dest='target', help='for validation or test dataset')

    if len(sys.argv) != 3:
        print 'Command e.g.: python makeFeature.py -t 0(1)'
        sys.exit(1)

    para = parser.parse_args()
    if para.target == 0:
        data_file = settings["TRAIN_DATA_FILE"]
        user_feature_file = settings["USER_CLUSTER_TRAIN_FILE"]
        item_feature_file = settings["ITEM_CLUSTER_TRAIN_FILE"]
    elif para.target == 1:
        data_file = settings["TAR_DATA_FILE"]
        user_feature_file = settings["USER_CLUSTER_TRAIN_FILE_FOR_SUBMIT"]
        item_feature_file = settings["ITEM_CLUSTER_TRAIN_FILE_FOR_SUBMIT"]
    else:
        print 'Invalid train data target choice...'
        sys.exit(1)

    data = [entry for entry in csv.reader(open(data_file))]
    data = [map(int, entry) for entry in data[1:]]
    uid_dict = getAttrDict(data, 0)
    pid_dict = getAttrDict(data, 1)
    user_features = genUserFeatures(data, pid_dict)
    item_features = genItemFeatures(data, uid_dict)

    writer = csv.writer(open(user_feature_file, "w"), lineterminator='\n')
    user_features = [[uid]+user_features[uid] for uid in user_features]
    writer.writerows(user_features)
    #for uid in user_features:
    #    writer.writerow([uid]+user_features[uid])
    writer = csv.writer(open(item_feature_file, "w"), lineterminator='\n')
    item_features = [[pid]+item_features[pid] for pid in item_features]
    print item_features[500]
    writer.writerows(item_features)
    #for pid in item_features:
    #    writer.writerow([pid]+item_features[pid])


if __name__ == "__main__":
    main()

