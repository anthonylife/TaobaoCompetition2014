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
# Date: 2014/3/17                                                 #
# Compute the precision, recall and F-score for evaluation        #
###################################################################

import os, sys, csv, json, argparse
from collections import defaultdict

settings = json.loads(open("../SETTINGS.json").read())
test_ins_file = "./libmf-1.0/testdata.dat"
result_file = "./libmf-1.0/output.dat"
traindata_convert_cmd = "./libmf-1.0/libmf convert " + \
        settings["LIBMF_TRAIN_FILE"] + " ./libmf-1.0/traindata.bin"
testdata_convert_cmd = "./libmf-1.0/libmf convert " + test_ins_file + \
        " ./libmf-1.0/testdata.bin"
train_cmd = "./libmf-1.0/libmf train --tr-rmse --obj -k 40 -t 200 -s 1 -p 0.05 -q 0.05 -g 0.03 -blk 1x1 -ub 1 -ib 1 --use-avg --no-rand-shuffle ./libmf-1.0/traindata.bin ./libmf-1.0/tr.model"
test_cmd = "./libmf predict ./libmf-1.0/testdata.bin ./libmf-1.0/tr.model " + result_file


def genTestFile():
    uid_set = set([])
    pid_set = set([])
    for entry in open(settings["LIBMF_TRAIN_FILE"]):
        uid = entry.split(" ")[0]
        pid = entry.split(" ")[1]
        uid_set.add(uid)
        pid_set.add(pid)
    wfd = open(test_ins_file, "w")
    for uid in uid_set:
        for pid in pid_set:
            wfd.write("%d %d\n" % (uid, pid))
    wfd.close()


def genResultFile():


def main():
    genTestFile()
    os.system(traindata_convert_cmd)
    os.system(testdata_convert_cmd)
    os.system(train_cmd)
    os.system(test_cmd)
    genResultFile()

if __name__ == "__main__":
    main()
