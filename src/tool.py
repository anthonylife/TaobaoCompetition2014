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
# contain some useful functions                                   #
###################################################################

import sys, csv, json

settings = json.loads(open("/home/anthonylife/Doctor/Code/Competition/taobao2014/SETTINGS.json").read())

def calSegNum(month, day):
    if month == 4:
        return 1
    elif month == 5 and day < 15:
        return 1
    elif month == 5 and day >= 15:
        return 2
    elif month == 6 and day < 15:
        return 2
    elif month == 6 and day >= 15:
        return 3
    elif month == 7 and day < 15:
        return 3
    elif month == 7 and day >= 15:
        return 4
    elif month == 8 and day <= 15:
        return 4
    else:
        print 'date exceed specified range...'
        sys.exit(1)

def getAverageUserBuy(topk):
    data = [feature for feature in csv.reader(open(settings["TRAIN_DATA_FILE"]))]
    data = [map(int, feature) for feature in data[1:]]

    user_average_buy = {}
    if topk == 0:
        user_buy = {}
        for entry in data:
            action_type = entry[2]
            if action_type == settings["ACTION_BUY"]:
                uid = entry[0]
                pid = entry[1]
                month = entry[3]
                day = entry[4]
                segnum = calSegNum(month, day)
                if uid in user_buy:
                    user_buy[uid][0].add(pid)
                    user_buy[uid][1].add(segnum)
                else:
                    user_buy[uid] = [set([pid]), set([segnum])]

        for uid in user_buy:
            user_average_buy[uid] = (len(user_buy[uid][0])+len(user_buy[uid][1])-1)/len(user_buy[uid][1])

    else:
        for entry in data:
            uid = entry[0]
            action_type = entry[2]
            if action_type == settings["ACTION_BUY"]:
                if uid not in user_average_buy:
                    user_average_buy[uid] = topk
    return user_average_buy


def combineFeature(data1, data2):
    return [entry1+entry2 for entry1, entry2 in zip(data1, data2)]


def calMonthLength(month, day):
    day_dif = 0
    if month == 4:
        day_dif = day - 14
    else:
        day_dif = 14 + day + (month-5)*30
    return 1.0*day_dif/30

