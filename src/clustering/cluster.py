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
# Cluster users and items based on their interaction history      #
###################################################################

import csv, json, sys, argparse
sys.path.append("../")
import data_io
from sklearn.cluster import KMeans

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
        user_features = [entry for entry in csv.reader(open(settings["USER_CLUSTER_TRAIN_FILE"]))]
        item_features = [entry for entry in csv.reader(open(settings["ITEM_CLUSTER_TRAIN_FILE"]))]
    elif para.target == 1:
        user_features = [entry for entry in csv.reader(open(settings["USER_CLUSTER_TRAIN_FILE_FOR_SUBMIT"]))]
        item_features = [entry for entry in csv.reader(open(settings["ITEM_CLUSTER_TRAIN_FILE_FOR_SUBMIT"]))]
    else:
        print 'Invalid train data target choice...'
        sys.exit(1)
    user_features = [map(int, entry[1:]) for entry in user_features]
    item_features = [map(int, entry[1:]) for entry in item_features]

    cluster = KMeans(n_clusters=para.ucluster_num)
    cluster.fit(user_features)
    data_io.save_model(cluster, settings["USER_CLUSTER_MODEL_FILE"])

    cluster = KMeans(n_clusters=para.icluster_num)
    cluster.fit(item_features)
    data_io.save_model(cluster, settings["ITEM_CLUSTER_MODEL_FILE"])


if __name__ == "__main__":
    main()

