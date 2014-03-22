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
# Pairwise learning                                               #
# Key points: 1.BPR learning                                      #
#             2.Multiple sampling strategy                        #
#             3.Various user behavior                             #
###################################################################

import numpy as np
import json, csv, sys, random
sys.path.append("../")
from collections import defaultdict
from tool import rZero, rGaussian, logisticLoss
from data_io import write_submission

settings = json.loads(open("../../SETTINGS.json").read())


class BPR():
    def __init__(self):
        # Control variable setting
        self.niters = 200

        # Hyper-parameter and
        self.ndim = 10
        self.lr = 0.05
        self.reg_user = 0.05
        self.reg_product = 0.05
        self.nsample = 3

    def model_init(self, train_file, init_choice):
        self.uid_set = set([])
        self.pid_set = set([])
        self.user_behavior = {}
        self.user_factor = {}
        self.product_factor = {}
        self.train_ins = [map(int, feature) for feature in
                csv.reader(open(settings['BPR_TRAIN_FILE']))]

        init_para = None
        if init_choice == settings["BPR_INIT_ZERO"]:
            init_para = rZero
        elif init_choice == settings["BPR_INIT_GAUSSIAN"]:
            init_para = rGaussian
        else:
            print 'Choice of model initialization error.'
            sys.exit(1)

        for entry in self.train_ins:
            uid = int(entry[0])
            pid = int(entry[1])
            val = int(entry[2])

            if uid not in self.uid_set:
                self.uid_set.add(uid)
            if pid not in self.pid_set:
                self.pid_set.add(pid)
            if uid not in self.user_behavior:
                self.user_behavior[uid] = [set(), set()]
            self.user_behavior[uid][val].add(pid)
            if uid not in self.user_factor:
                self.user_factor[uid] = np.arrays(init_para(self.ndim))
            if pid not in self.product_factor:
                self.product_factor[pid] = np.arrays(init_para(self.ndim))
            self.uid_set = list(self.uid_set)

        for uid in self.user_behavior:
            self.user_behavior[uid][2] = list(self.user_behavior[uid][0])
            self.user_behavior[uid][3] = list(self.user_behavior[uid][1])

    def generateTrainPairs(self, sample_method, uid, pid, index, neg_pid_set):
        train_pairs = []
        if sample_method == settings["BPR_SAMPLE_TRIPLE"]:
            clicked_product = self.user_behavior[uid][2][index]
            train_pairs.append([pid, clicked_product])
            for neg_pid in neg_pid_set:
                train_pairs.append(pid, neg_pid)
                train_pairs.append(neg_pid_set, neg_pid)
        elif sample_method == settings["BPR_SAMPLE_TUPLE"]:
            for neg_pid in neg_pid_set:
                train_pairs.append(pid, neg_pid)
        return train_pairs


    def train(self, sample_method):
        for i in xrange(self.niters):
            random.shuffle(self.uid_set)
            for uid in self.uid_set:
                random.shuffle(self.user_behavior[uid][2])
                random.shuffle(self.user_behavior[uid][3])
                neg_pid_set = random.sample(self.pid_set-self.user_behavior[uid][2]
                        -self.user_behavior[uid][3], self.nsample)
                #for pid in self.user_behavior[uid][0]:
                for i, pid in enumerate(self.user_behavior[uid][1]):
                    train_pairs = self.generateTrainPairs(sample_method, uid,
                            pid, i, neg_pid_set)
                    for pair in train_pairs:
                        pos_score = self.user_factor[uid]*self.product_factor[pair[0]]
                        neg_score = self.user_factor[uid]*self.product_factor[pair[1]]
                        tmp_loss = logisticLoss(pos_score, neg_score)
                        self.user_factor[uid] = self.user_factor[uid] + self.lr*(tmp_loss*(self.product_factor[pair[0]]-self.product_factor[pair[1]])-self.reg_user*self.user_factor[uid])
                        self.product_factor[pair[0]] = self.product_factor[pair[0]]+self.lr(tmp_loss*self.user_factor[uid]-self.reg_product*self.product_factor[pair[0]])
                        self.product_factor[pair[1]] = self.product_factor[pair[1]]+self.lr(tmp_loss*(-self.user_factor[uid])-self.reg_product*self.product_factor[pair[1]])
            #print "\rCurrent iteration %d..." % (i+1)
            print "\rCurrent iteration %d, AUC is %f..." % (i+1, self.evaluation())
            raw_input()
        self.save_model()

    def evaluation(self):
        total_pair = 0
        correct_pair = 0
        for uid in self.user_behavior:
            for pos_pid in self.user_behavior[uid][1]:
                for neg_pid in self.user_behavior[uid][0]:
                    total_pair += 1
                    diff_score = self.user_factor[uid]*self.product_factor[pos_pid]-self.user_factor[uid]-self.product_factor[neg_pid]
                    if diff_score > 0:
                        correct_pair += 1
        return 1.0*correct_pair/total_pair

    def genRecommendResult(self, restart, topk, train_file, init_choice):
        if not restart:
            self.model_init()
            self.load_model()
        recommend_result = defaultdict(list)
        for uid in self.uid_set:
            tmp_result = []
            sorted_result = []
            for pid in self.pid_set:
                score = self.user_factor[uid]*self.product_factor[pid]
                tmp_result.append([pid, score])
            sorted_result = [entry[0] for entry in sorted(tmp_result, key=lambda x:x[1], reverse=True)]
            recommend_result[uid] = sorted_result[:topk]
        write_submission(recommend_result)

    def save_model(self):
        writer = csv.writer(open(settings["MODEL_USER_FILE"], "w"), lineterminator="\n")
        for uid in self.user_factor:
            writer.writerow([uid]+self.user_factor[uid])
        writer = csv.writer(open(settings["MODEL_PRODUCT_FILE"], "w"), lineterminator="\n")
        for pid in self.product_factor:
            writer.writerow([pid]+self.product_factor[pid])

    def load_model(self):
        self.user_factor = {}
        for entry in csv.reader(open(settings["MODEL_USER_FILE"])):
            uid = int(entry[0])
            factor = np.array(map(float, entry[1:]))
            self.user_factor[uid] = factor

        self.product_factor = {}
        for entry in csv.reader(open(settings["MODEL_PRODUCT_FILE"])):
            pid = int(entry[0])
            factor = np.array(map(float, entry[1:]))
            self.product_factor[pid] = factor

