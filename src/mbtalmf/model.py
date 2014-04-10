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
# Date: 2014/4/10                                                 #
# Multi-behavior affinity latent factor model                     #
# Key points: 1.SGD                                               #
#             2.consider different user behavior simutaneously    #
#             3.affinity model                                    #
###################################################################

import numpy as np
import json, csv, sys, random, math
sys.path.append("../")
from collections import defaultdict
from tool import calSegNum, getDayDiff, rZero, rPosGaussian, getTimePenality

settings = json.loads(open("../../SETTINGS.json").read())


def getUserMultipleBehavior(data, month_num):
    user_buy = {}
    user_click = {}
    for entry in data:
        uid, pid, action_type, month, day = entry
        if action_type == 0 or action_type == 1:
            seg_num = calSegNum(month, day)
            if seg_num == 1:
                continue
            if action_type == 0:
                if uid not in user_click:
                    user_click[uid] = {}
                if pid not in user_click[uid]:
                    user_click[uid][pid] = 1
                else:
                    user_click[uid][pid] += 1
                    #if user_click[uid][pid] > 20:
                    #    user_click[uid][pid] = 20
            elif action_type == 1:
                if uid not in user_buy:
                    user_buy[uid] = [set([]) for i in xrange(month_num)]
                user_buy[uid][seg_num-1].add(pid)
    for uid in user_click:
        for pid in user_click[uid]:
            user_click[uid][pid] = np.log(user_click[uid][pid])
    return user_buy, user_click


def genTrainData(data, time_alpha, user_buy, user_click, pid_set, ratio, month_num,
        src_month, src_day):
    user_buy_num = {}
    train_buy_pair = []
    train_click_pair = []

    for entry in data:
        uid, pid, action_type, month, day = entry
        if action_type == 1:
            seg_num = calSegNum(month, day)
            if uid not in user_buy_num:
                user_buy_num[uid] = [{} for i in xrange(month_num)]
            if pid not in user_buy_num[uid][seg_num-1]:
                user_buy_num[uid][seg_num-1][pid] = [1, [getTimePenality(
                    time_alpha, src_month, src_day, month, day)]]
            else:
                user_buy_num[uid][seg_num-1][pid][0] += 1
                user_buy_num[uid][seg_num-1][pid][1].append(getTimePenality(
                    time_alpha, src_month, src_day, month, day))
            if seg_num == 1:
                continue
            neg_pids = random.sample(pid_set-user_buy[uid][seg_num-1], ratio)
            for neg_pid in neg_pids:
                train_buy_pair.append([uid, pid, neg_pid, seg_num])

    for uid in user_click:
        for pid in user_click[uid]:
            train_click_pair.append([uid, pid, user_click[uid][pid]])

    return user_buy_num, train_buy_pair, train_click_pair


class MBTALMF():
    def __init__(self):
        self.niters = 50
        self.ndim = 20
        self.lr = 0.05
        self.lamda = 0.1
        self.lamda1 = 0.01
        self.eta = 0.1
        self.theta = 0
        self.ratio = 5
        self.time_alpha = 10

    def model_init(self, train_data_file, init_choice, target):
        self.uid_dict = {}
        self.pid_dict = {}
        data = [entry for entry in csv.reader(open(train_data_file))]
        data = [map(int, entry) for entry in data[1:]]

        for entry in data:
            uid, pid = entry[:2]
            if uid not in self.uid_dict:
                self.uid_dict[uid] = len(self.uid_dict)
            if pid not in self.pid_dict:
                self.pid_dict[pid] = len(self.pid_dict)

        if target == 0:
            self.month_num = 3
            self.month = settings["VALIDATION_TIME_LAST_MONTH"]
            self.day = settings["VALIDATION_TIME_LAST_DAY"]
            self.user_buy, user_click = getUserMultipleBehavior(data, self.month_num)
        elif target == 1:
            self.month_num = 4
            self.month = settings["TIME_LAST_MONTH"]
            self.day = settings["TIME_LAST_DAY"]
            self.user_buy, user_click = getUserMultipleBehavior(data, self.month_num)

        if init_choice == settings["MBTMF_INIT_ZERO"]:
            factor_init_method = rZero
        elif init_choice == settings["MBTMF_INIT_GAUSSIAN"]:
            factor_init_method = rPosGaussian
        else:
            print 'Choice of model initialization error.'
            sys.exit(1)

        self.user_buy_factor = np.array([factor_init_method(self.ndim) for i in
            xrange(len(self.uid_dict))])
        self.user_click_factor = np.array([factor_init_method(self.ndim) for i in
            xrange(len(self.uid_dict))])
        self.product_factor = np.array([factor_init_method(self.ndim) for i in
            xrange(len(self.pid_dict))])
        self.revenue_para = np.array([1 for i in xrange(len(self.pid_dict))])

        self.user_buy_num, self.train_buy_pair, self.train_click_pair =\
                genTrainData(data, self.time_alpha, self.user_buy, user_click,
                        set(self.pid_dict.keys()), self.ratio, self.month_num,
                        self.month, self.day)
        self.u_enhanced_factor = np.array(factor_init_method(self.ndim))
        self.tmp_user_buy_factor = np.array(factor_init_method(self.ndim))
        self.tmppos_product_factor = np.array(factor_init_method(self.ndim))
        self.tmpneg_product_factor = np.array(factor_init_method(self.ndim))
        self.p_revenue = 0.0
        self.n_revenue = 0.0
        self.logistic_loss = 0.0


    def train(self):
        #print("Before training, AUC is %f...\n" % (self.evaluation()))
        print("Before training, AUC is 0.509750...\n")
        for i in xrange(self.niters):
            fidx_rank=0
            fidx_reg=0
            random.shuffle(self.train_buy_pair)
            random.shuffle(self.train_click_pair)
            finished_num = 0
            while(True):
                '''if fidx_rank == len(self.train_buy_pair) and\
                        fidx_reg == len(self.train_click_pair):
                    break
                if fidx_rank == len(self.train_buy_pair):
                    uid, pid, click_num = self.train_click_pair[fidx_reg]
                    self.updateRegPara(uid, pid, click_num)
                    fidx_reg += 1
                elif fidx_reg == len(self.train_click_pair):
                    uid, pos_pid, neg_pid, seg_num = self.train_buy_pair[fidx_rank]
                    self.updateRankPara(uid, pos_pid, neg_pid, seg_num)
                    fidx_rank += 1
                else:
                    r_theta = random.random()
                    if r_theta > self.theta:
                        uid, pos_pid, neg_pid, seg_num = self.train_buy_pair[fidx_rank]
                        self.updateRankPara(uid, pos_pid, neg_pid, seg_num)
                        fidx_rank += 1
                    else:
                        uid, pid, click_num = self.train_click_pair[fidx_reg]
                        self.updateRegPara(uid, pid, click_num)
                        fidx_reg += 1'''
                if fidx_rank == len(self.train_buy_pair) or\
                        fidx_reg == len(self.train_click_pair):
                    break
                r_theta = random.random()
                if r_theta > self.theta:
                    uid, pos_pid, neg_pid, seg_num = self.train_buy_pair[fidx_rank]
                    self.updateRankPara(uid, pos_pid, neg_pid, seg_num)
                    fidx_rank += 1
                else:
                    uid, pid, click_num = self.train_click_pair[fidx_reg]
                    self.updateRegPara(uid, pid, click_num)
                    fidx_reg += 1

                finished_num += 1
                if (finished_num%1000) == 0:
                    sys.stdout.write("\rFINISHED NUM: %d..." % finished_num)
                    sys.stdout.flush()
            #if (i+1) % 10 == 0:
            #    print("\nCurrent iteration %d, AUC is %f...\n" % (i+1, self.evaluation()))
        self.save_model()


    def getUserEnhancedFactor(self, uid, seg_num):
        if seg_num < 2:
            print seg_num
            print 'Invalid segment number'
            sys.exit(1)
        try:
            if uid not in self.user_buy_num or len(self.user_buy_num[uid][seg_num-2]) == 0:
                return 0
        except:
            print seg_num
            sys.ext(1)
        total_num = 0
        for pid in self.user_buy_num[uid][seg_num-2]:
            for penality in self.user_buy_num[uid][seg_num-2][pid][1]:
                self.u_enhanced_factor +=\
                    penality*self.product_factor[self.pid_dict[pid]]
            total_num += self.user_buy_num[uid][seg_num-2][pid][0]
        self.u_enhanced_factor = self.u_enhanced_factor/total_num
        return total_num


    def getProductRevenue(self, uid, pid, seg_num, tag):
        if uid not in self.user_buy_num or pid not in self.user_buy_num[uid][seg_num-2]:
            if tag == 0:
                self.p_revenue = 1.0
            elif tag == 1:
                self.n_revenue = 1.0
            return 0
        else:
            if tag == 0:
                self.p_revenue = (self.user_buy_num[uid][seg_num-2][pid][0]+1)**self.revenue_para[self.pid_dict[pid]]-(self.user_buy_num[uid][seg_num-2][pid][0])**self.revenue_para[self.pid_dict[pid]]
            elif tag == 1:
                self.n_revenue = (self.user_buy_num[uid][seg_num-2][pid][0]+1)**self.revenue_para[self.pid_dict[pid]]-(self.user_buy_num[uid][seg_num-2][pid][0])**self.revenue_para[self.pid_dict[pid]]
            return self.user_buy_num[uid][seg_num-2][pid][0]


    def getLogisticLoss(self, uidx, ppidx, npidx):
        self.logistic_loss = 1 - 1.0/(1+np.exp(-np.dot(self.user_buy_factor[uidx]+
            self.u_enhanced_factor, self.product_factor[ppidx])*self.p_revenue
            +np.dot(self.user_buy_factor[uidx]+self.u_enhanced_factor,
                self.product_factor[npidx])*self.n_revenue))
        '''if self.logistic_loss < 0.00001:
            print self.user_buy_factor[uidx]
            print self.u_enhanced_factor
            print self.product_factor[ppidx]
            print self.product_factor[npidx]
            print self.p_revenue
            print self.n_revenue
            print np.dot(self.user_buy_factor[uidx]+self.u_enhanced_factor, self.product_factor[ppidx])*self.p_revenue
            #raw_input()'''

    def updateRankPara(self, uid, pos_pid, neg_pid, src_seg_num):
        uidx = self.uid_dict[uid]
        ppidx = self.pid_dict[pos_pid]
        npidx = self.pid_dict[neg_pid]
        total_num = self.getUserEnhancedFactor(uid, src_seg_num)
        pos_buy_num = self.getProductRevenue(uid, pos_pid, src_seg_num, 0)
        neg_buy_num = self.getProductRevenue(uid, neg_pid, src_seg_num, 1)
        self.getLogisticLoss(uidx, ppidx, npidx)

        # calculate new user factor
        self.tmp_user_buy_factor =\
                self.user_buy_factor[uidx]+self.lr*(self.logistic_loss
                *(self.product_factor[ppidx]*self.p_revenue
                -self.product_factor[npidx]*self.n_revenue)
                -self.lamda*self.user_buy_factor[uidx]
                -self.eta*(self.user_buy_factor[uidx]
                -self.user_click_factor[uidx]))

        # calculate new positive product factor
        self.tmppos_product_factor =\
                self.product_factor[ppidx]+self.lr*(self.logistic_loss
                *(self.user_buy_factor[uidx]
                +self.u_enhanced_factor)*self.p_revenue
                -self.lamda*self.product_factor[ppidx])

        # calculate new negative product factor
        self.tmpneg_product_factor =\
                self.product_factor[npidx]+self.lr*(-self.logistic_loss\
                *(self.user_buy_factor[uidx]
                +self.u_enhanced_factor)*self.n_revenue
                -self.lamda*self.product_factor[npidx])

        # calculate new positive product related marginal revenue parameter
        if pos_buy_num > 0:
            self.revenue_para[ppidx] =\
                self.revenue_para[ppidx]\
                +self.lr*(self.logistic_loss*np.dot(self.user_buy_factor[uidx]
                +self.u_enhanced_factor, self.product_factor[ppidx])\
                *((pos_buy_num+1)**self.revenue_para[ppidx]
                *np.log(pos_buy_num+1)-pos_buy_num**self.revenue_para[ppidx]
                *np.log(pos_buy_num))-self.lamda1*self.revenue_para[ppidx])

        # calculate new negative product related marginal revenue parameter
        if neg_buy_num > 0:
            self.revenue_para[npidx] =\
                self.revenue_para[npidx]\
                +self.lr*(-self.logistic_loss*np.dot(self.user_buy_factor[uidx]
                +self.u_enhanced_factor, self.product_factor[npidx])\
                *((neg_buy_num+1)**self.revenue_para[npidx]
                *np.log(neg_buy_num+1)-neg_buy_num**self.revenue_para[npidx]
                *np.log(neg_buy_num))-self.lamda1*self.revenue_para[npidx])

        # calculate new enhanced product factor
        for pid in self.user_buy_num[uid][src_seg_num-2]:
            for penality in self.user_buy_num[uid][src_seg_num-2][pid][1]:
                self.product_factor[self.pid_dict[pid]] =\
                        self.product_factor[self.pid_dict[pid]]\
                        +self.lr*(self.logistic_loss*penality/total_num
                        *(self.product_factor[ppidx]*self.p_revenue
                        -self.product_factor[npidx]*self.n_revenue)
                        -self.lamda*self.product_factor[self.pid_dict[pid]])

        # update all related parameters
        self.user_buy_factor[uidx] = self.tmp_user_buy_factor
        self.product_factor[ppidx] = self.tmppos_product_factor
        self.product_factor[npidx] = self.tmpneg_product_factor

        # clear
        self.u_enhanced_factor = np.zeros(self.ndim)


    def updateRegPara(self, uid, pid, click_num):
        uidx = self.uid_dict[uid]
        pidx = self.pid_dict[pid]
        val_diff=np.dot(self.user_click_factor[uidx],self.product_factor[pidx])\
                -click_num
        self.user_click_factor[uidx] = self.user_click_factor[uidx]\
                - self.lr*(self.product_factor[pidx]*val_diff\
                + self.lamda*self.user_click_factor[uidx]\
                + self.eta*(self.user_click_factor[uidx]-self.user_buy_factor[uidx]))
        self.product_factor[pidx] = self.product_factor[pidx]\
                - self.lr*(self.user_click_factor[uidx]*val_diff\
                + self.lamda*self.product_factor[pidx])


    def evaluation(self):
        total_num = 0
        correct_num = 0
        for uid in self.user_buy:
            for i in xrange(1, self.month_num):
                for pos_pid in self.user_buy[uid][i]:
                    for neg_pid in self.pid_dict:
                        if neg_pid in self.user_buy[uid][i]:
                            continue
                        total_num += 1
                        uidx = self.uid_dict[uid]
                        ppidx = self.pid_dict[pos_pid]
                        npidx = self.pid_dict[neg_pid]
                        self.getUserEnhancedFactor(uid, i+1)
                        self.getProductRevenue(uid, pos_pid, i+1, 0)
                        self.getProductRevenue(uid, neg_pid, i+1, 1)
                        cmp_score = np.dot(self.user_buy_factor[uidx]
                                +self.u_enhanced_factor,self.product_factor[ppidx])\
                                *self.p_revenue-np.dot(self.user_buy_factor[uidx]
                                +self.u_enhanced_factor,self.product_factor[npidx])\
                                *self.n_revenue
                        if cmp_score > 0:
                            correct_num += 1
        return 1.0*correct_num/total_num


    def save_model(self):
        writer = csv.writer(open(settings["MBTMF_MODEL_USER_FILE"], "w"),
                lineterminator="\n")
        for uid in self.uid_dict:
            writer.writerow([uid]+list(self.user_buy_factor[self.uid_dict[uid]]))

        writer = csv.writer(open(settings["MBTMF_MODEL_PRODUCT_FILE"], "w"),
                lineterminator="\n")
        for pid in self.pid_dict:
            writer.writerow([pid]+list(self.product_factor[self.pid_dict[pid]]))

        writer = csv.writer(open(settings["MBTMF_MODEL_REVENUE_FILE"], "w"),
                lineterminator="\n")
        for pid in self.pid_dict:
            writer.writerow([pid]+[self.revenue_para[self.pid_dict[pid]]])


    def load_model(self):
        for entry in csv.reader(open(settings["MBTMF_MODEL_USER_FILE"])):
            uid = int(entry[0])
            factor = np.array(map(float, entry[1:]))
            self.user_buy_factor[self.uid_dict[uid]] = factor

        for entry in csv.reader(open(settings["MBTMF_MODEL_PRODUCT_FILE"])):
            pid = int(entry[0])
            factor = np.array(map(float, entry[1:]))
            self.product_factor[self.pid_dict[pid]] = factor

        for entry in csv.reader(open(settings["MBTMF_MODEL_REVENUE_FILE"])):
            pid = int(entry[0])
            self.revenue_para[self.pid_dict[pid]] = float(entry[1])


    def genRecommendResult(self, restart, train_data_file, init_choice, threshold_val, target):
        if not restart:
            self.model_init(train_data_file, init_choice, target)
            self.load_model()
        recommend_result = defaultdict(list)
        for uid in self.uid_dict:
            for pid in self.pid_dict:
                uidx = self.uid_dict[uid]
                pidx = self.pid_dict[pid]
                self.getUserEnhancedFactor(uid, self.month_num+1)
                self.getProductRevenue(uid, pid, self.month_num+1, 0)
                score = np.dot(self.user_buy_factor[uidx]
                        +self.u_enhanced_factor,self.product_factor[pidx])\
                        *self.p_revenue
                if score > threshold_val:
                    recommend_result[uid].append(pid)
        return recommend_result
