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
# baseline: recommend products based on popularity of product     #
###################################################################

import sys, csv, json, argparse
from collections import defaultdict
from data_io import write_submission
from tool import getAverageUserBuy

settings = json.loads(open("../SETTINGS.json").read())


def genPopularList(train_file):
    data = [feature for feature in csv.reader(open(train_file))]
    data = [map(int, feature) for feature in data[1:]]

    popular_products = {}
    for entry in data:
        action_type = entry[2]
        if action_type == settings["ACTION_BUY"]:
            pid = entry[1]
            if pid in popular_products:
                popular_products[pid] += 1
            else:
                popular_products[pid] = 1
    popular_products = sorted(popular_products.items(), key=lambda x:x[1],
            reverse=True)
    popular_products = [entry[0] for entry in popular_products]
    return popular_products


def genRecommendResult(products, user_average_buy):
    recommend_result = defaultdict(list)
    for uid in user_average_buy:
        topk = user_average_buy[uid]
        recommend_result[uid] = products[:topk]
    return recommend_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-topk', type=int, action='store', dest='topk',
            help='specify the number of products to be recommended to\
                    users, 0 stands for using user personal average.')

    if len(sys.argv) != 3:
        print 'Command e.g.: python runPopularity -topk 5'
        sys.exit(1)
    para = parser.parse_args()

    products= genPopularList(settings["TRAIN_DATA_FILE"])
    user_average_buy = getAverageUserBuy(para.topk)
    recommend_result = genRecommendResult(products, user_average_buy)
    write_submission(recommend_result)

if __name__ == "__main__":
    main()
