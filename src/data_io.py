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
# Generate submission file                                        #
###################################################################

import sys, csv, json
import pickle

settings = json.loads(open("/home/anthonylife/Doctor/Code/Competition/taobao2014/SETTINGS.json").read())

def write_submission(user_recommend_result):
    wfd = open(settings["SUBMISSION_PATH"], "w")
    for uid in user_recommend_result:
        wfd.write("%d\t" % uid)
        for i, pid in enumerate(user_recommend_result[uid]):
            if i == len(user_recommend_result[uid])-1:
                wfd.write("%d\n" % pid)
            else:
                wfd.write("%d," % pid)
    wfd.close()

def save_model(model, out_path):
    pickle.dump(model, open(out_path, "w"))

def load_model(in_path):
    return pickle.load(open(in_path))

