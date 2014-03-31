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
# Date: 2014/3/31                                                 #
# Weighted Matrix Factorization                                   #
# Key points: 1.SGD and Alternating Least Square                  #
#             2.Different confidence                              #
#             3.Various user behavior                             #
###################################################################
import numpy as np
import json, csv, sys, random
sys.path.append("../")
from collections import defaultdict
from tool import getUserBehavior, getDayDiff, rZero, rGaussian

settings = json.loads(open("../../SETTINGS.json").read())
WEIGHT = [4, 4, 1]
TAR_MONTH = 7
TAR_DAY = 15
TIME_ALPHA = 0.2
INC_RATE = 10


class WMF():
    def __init__(self):
        self.niters = 10

        # for SGD
        self.ndim1 = 20
        self.lr1 = 0.05
        self.reg_user = 0.1
        self.reg_product = 0.1

        # for ALS
        self.ndim2 = 20
        self.lambda2 = 100

    def model_init(self, lr_method, train_file, init_choice):
        self.uid_dict = {}
        self.pid_dict = {}
        data = [entry for entry in csv.reader(open(train_file))]
        data = [map(int, entry) for entry in data[1:]]

        self.user_behavior = getUserBehavior(data)
        for entry in data:
            uid, pid = entry[:2]
            if uid not in self.uid_dict:
                self.uid_dict[uid] = len(self.uid_dict)
            if pid not in self.pid_dict:
                self.pid_dict[pid] = len(self.pid_dict)

        factor_init_method = None
        if init_choice == settings["WMF_INIT_ZERO"]:
            factor_init_method = rZero
        elif init_choice == settings["WMF_INIT_GAUSSIAN"]:
            factor_init_method = rGaussian
        else:
            print 'Choice of model initialization error.'
            sys.exit(1)

        if lr_method == settings["WMF_LR_ALS"]:
            self.user_factor = np.array([factor_init_method(self.ndim2) for i in
                xrange(len(self.uid_dict))])
            self.product_factor = np.array([factor_init_method(self.ndim2) for i in
                xrange(len(self.pid_dict))])
            self.als_model_init()
        elif lr_method == settings["WMF_LR_SGD"]:
            self.user_factor = np.array([factor_init_method(self.ndim1) for i in
                xrange(len(self.uid_dict))])
            self.product_factor = np.array([factor_init_method(self.ndim1) for i in
                xrange(len(self.pid_dict))])
            self.sgd_model_init()
        else:
            print 'Learning method choice invalid.'
            sys.exit(1)

    def cal_preference(self, cnt):
        if cnt > 0:
            return 1
        else:
            return 0

    def cal_confidence(self, cnt):
        return 1+INC_RATE*cnt


    def als_model_init(self):
        self.user_preference = {}
        self.user_confidence = {}
        for uid in self.user_behavior:
            pseudo_cnt = [0 for i in xrange(len(self.pid_dict))]
            for i in xrange(len(WEIGHT)):
                for entry in self.user_behavior[uid][i]:
                    pid, src_month, src_day = entry
                    pseudo_cnt[self.pid_dict[pid]] += WEIGHT[i]/(1+TIME_ALPHA*abs(getDayDiff(src_month, src_day, TAR_MONTH, TAR_DAY)))

            self.user_preference[uid] = np.array(map(self.cal_preference, pseudo_cnt))
            self.user_confidence[uid] = np.array(map(self.cal_confidence, pseudo_cnt))
            #print self.user_preference[uid][0:10]
            #print self.user_confidence[uid][0:10]
            #raw_input()

        self.product_preference = {}
        self.product_confidence = {}
        for pid in self.pid_dict:
            self.product_preference[pid] = np.array([0 for i in xrange(len(self.uid_dict))])
            self.product_confidence[pid] = np.array([0.0 for i in xrange(len(self.uid_dict))])
        for uid in self.user_preference:
            for pid in self.pid_dict:
                self.product_preference[pid][self.uid_dict[uid]] = self.user_preference[uid][self.pid_dict[pid]]
                self.product_confidence[pid][self.uid_dict[uid]] = self.user_confidence[uid][self.pid_dict[pid]]


    def cal_confidence1(self, cnt):
        pass

    def sgd_model_init(self):
        pass


    def train(self, lr_method):
        for i in xrange(self.niters):
            if lr_method == settings["WMF_LR_ALS"]:
                self.als_train()
            elif lr_method == settings["WMF_LR_SGD"]:
                self.sgd_train()
            else:
                print 'Learning method choice invalid.'
                sys.exit(1)
            print 'Iteration %d, RMSE %f' % (i+1, self.evaluation())


    def als_train(self):
        for i, uid in enumerate(self.uid_dict):
            sys.stdout.write("\rFINISHED UID NUM: %d" % (i+1))
            sys.stdout.flush()
            uidx = self.uid_dict[uid]
            self.user_factor[uidx] = np.dot(np.dot(np.dot(np.linalg.inv(np.dot(np.dot(np.transpose(self.product_factor), np.diag(self.user_confidence[uid])), self.product_factor)+self.lambda2*np.eye(self.ndim2)), np.transpose(self.product_factor)), np.diag(self.user_confidence[uid])), np.transpose(self.user_preference[uid]))
        for i, pid in enumerate(self.pid_dict):
            sys.stdout.write("\rFINISHED PID NUM: %d" % (i+1))
            sys.stdout.flush()
            pidx = self.pid_dict[pid]
            self.product_factor[pidx] = np.dot(np.dot(np.dot(np.linalg.inv(np.dot(np.dot(np.transpose(self.user_factor),np.diag(self.product_confidence[pid])), self.user_factor)+self.lambda2*np.eye(self.ndim2)), np.transpose(self.user_factor)),np.diag(self.product_confidence[pid])),np.transpose(self.product_preference[pid]))


    def evaluation(self):
        rmse = 0.0
        divider = 0
        for uid in self.uid_dict:
            for pid in self.pid_dict:
                pred_score = np.dot(self.user_factor[self.uid_dict[uid]], self.product_factor[self.pid_dict[pid]])
                rmse += self.user_confidence[uid][self.pid_dict[pid]]*np.square(pred_score-self.user_preference[uid][self.pid_dict[pid]])
                divider += self.user_confidence[uid][self.pid_dict[pid]]
        rmse = np.sqrt(rmse/divider)
        return rmse


    def save_model(self):
        writer = csv.writer(open(settings["WMF_MODEL_USER_FILE"], "w"), lineterminator="\n")
        for uid in self.uid_dict:
            writer.writerow([uid]+list(self.user_factor[self.uid_dict[uid]]))

        writer = csv.writer(open(settings["WMF_MODEL_PRODUCT_FILE"], "w"), lineterminator="\n")
        for pid in self.pid_dict:
            writer.writerow([pid]+list(self.product_factor[self.pid_dict[pid]]))


    def load_model(self):
        for entry in csv.reader(open("WMF_MODEL_USER_FILE")):
            uid = int(entry[0])
            factor = np.array(map(float, entry[1:]))
            self.user_factor[self.uid_dict[uid]] = factor

        for entry in csv.reader(open("WMF_MODEL_PRODUCT_FILE")):
            pid = int(entry[0])
            factor = np.array(map(float, entry[1:]))
            self.product_factor[self.pid_dict[pid]] = factor


    def genRecommendResult(self, restart, lr_method, train_file, init_choice, threshold_val):
        if not restart:
            self.model_init(lr_method, train_file, init_choice)
            self.load_model()
        recommend_result = defaultdict(list)
        for uid in self.uid_dict:
            for pid in self.pid_dict:
                score = np.dot(self.user_factor[self.uid_dict[uid]], self.product_factor[self.pid_dict[pid]])
                if score > threshold_val:
                    recommend_result.append(pid)
        return recommend_result

