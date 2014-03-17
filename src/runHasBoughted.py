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
# baseline: recommend products users broughted                    #
###################################################################

import sys, csv, json
from collections import defaultdict
from data_io import write_submission

settings = json.loads(open("../SETTINGS.json").read())


def genUserBrought(train_file):
    data = [feature for feature in csv.reader(open(train_file))]
    data = [map(int, feature) for feature in data[1:]]

    user_bought = defaultdict(set)
    for entry in data:
        action_type = entry[2]
        if action_type == settings["ACTION_BUY"]:
            uid = entry[0]
            pid = entry[1]
            user_bought[uid].add(pid)
    return user_bought


def main():
    user_bought = genUserBrought(settings["TRAIN_DATA_FILE"])
    write_submission(user_bought)


if __name__ == "__main__":
    main()
