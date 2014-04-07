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
# Date: 2014/4/4                                                  #
# Predict the cluster label for each user and product             #
###################################################################

import sys, csv, json, argparse
sys.path.append("../")
import data_io

settings = json.loads(open("../../SETTINGS.json").read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=int, action='store',
            dest='target', help='for validation or test dataset')
    parser.add_argument('-c1', type=int, action='store',
            dest='ucluster_num', help='cluster number of users')
    parser.add_argument('-c2', type=int, action='store',
            dest='icluster_num', help='cluster number of items')

    if len(sys.argv) != 7:
        print 'Command e.g.: python cluster.py -t 0(1) -c1 20 -c2 50'
        sys.exit(1)

    para = parser.parse_args()
    if para.target == 0:
        user_features = [map(int, entry) for entry in csv.reader(open(settings["USER_CLUSTER_TRAIN_FILE"]))]
        item_features = [map(int, entry) for entry in csv.reader(open(settings["ITEM_CLUSTER_TRAIN_FILE"]))]
        user_cluster_file = settings["USER_CLUSTER_TEST_FILE"]
        item_cluster_file = settings["ITEM_CLUSTER_TEST_FILE"]
    elif para.target == 1:
        user_features = [map(int, entry) for entry in csv.reader(open(settings["USER_CLUSTER_TRAIN_FILE_FOR_SUBMIT"]))]
        item_features = [map(int, entry) for entry in csv.reader(open(settings["ITEM_CLUSTER_TRAIN_FILE_FOR_SUBMIT"]))]
        user_cluster_file = settings["USER_CLUSTER_TEST_FILE_FOR_SUBMIT"]
        item_cluster_file = settings["ITEM_CLUSTER_TEST_FILE_FOR_SUBMIT"]
    else:
        print 'Invalid train data target choice...'
        sys.exit(1)

    writer = csv.writer(open(user_cluster_file, "w"), lineterminator="\n")
    cluster = data_io.load_model(settings["USER_CLUSTER_MODEL_FILE"])
    uids = [entry[0] for entry in user_features]
    features = [entry[1:] for entry in user_features]
    labels = cluster.predict(features)
    for uid, label in zip(uids, labels):
        writer.writerow([uid, label])

    writer = csv.writer(open(item_cluster_file, "w"), lineterminator="\n")
    cluster = data_io.load_model(settings["ITEM_CLUSTER_MODEL_FILE"])
    pids = [entry[0] for entry in item_features]
    features = [entry[1:] for entry in item_features]
    labels = cluster.predict(features)
    for pid, label in zip(pids, labels):
        writer.writerow([pid, label])

if __name__ == "__main__":
    main()


