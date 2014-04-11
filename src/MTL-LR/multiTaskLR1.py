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
# Mean Regularized Multi-Task Learning with LR model              #
###################################################################

import csv, sys, json, random
sys.path.append("../")
import numpy as np
from tool import rZero, rGaussian, logisticVal

settings = json.loads(open("../../SETTINGS.json").read())


class MeanRegularizedMultiTaskLR():
    def __init__(self, C=1, tol=0.0001, intercept_scaling=1, lr = 0.01, eta=1,
            field_for_model_num=1, max_niters = 500, confidence = 50,
            para_init="gaussian", global_model_file=settings["GBT_MODEL_PARA_FILE"]):
        self.C = C
        self.tol = tol
        self.intercept = intercept_scaling
        self.lr = lr
        self.eta = eta
        self.field_for_model_num = field_for_model_num-1
        self.max_niters = max_niters
        self.confidence = confidence
        self.global_model_file = global_model_file
        if para_init == settings["MTLR_INIT_GAUSSIAN"]:
            self.para_init_method = rGaussian
        elif para_init == settings["MTLR_INIT_ZERO"]:
            self.para_init_method = rZero
        else:
            print 'Invalid method choice of parameter initialization'
            sys.exit(1)


    def fit(self, pairs, features, targets):
        self.features = np.array([feature for feature in features])
        self.pairs = pairs
        if not np.all(targets>-1):
            print 'Data label = -1 or = 1'
            sys.exit(1)
        self.targets = np.array(targets)

        if len(self.features) != len(self.targets):
            print 'Mismatch for number of features and number of targets'
            sys.exit(1)
        self.nInstance = len(self.targets)
        self.createMultiModel1()
        global_para = np.array([map(float, entry) for entry in csv.reader(open(self.global_model_file))])
        self.global_para = global_para[0]
        if len(self.global_para) != self.feature_dim:
            print self.global_para
            print len(self.global_para), self.feature_dim
            print 'Global parameter dimension and local parameter mismatch...'
            sys.exit(1)

        visit_idxs = [i for i in xrange(self.nInstance)]
        last_loglikelihood = 0.0
        for ii in xrange(self.max_niters):
            random.shuffle(visit_idxs)
            finished_num = 0
            for idx in visit_idxs:
                feature = self.features[idx]
                target = self.targets[idx]
                if self.pairs[idx][self.field_for_model_num] in self.val_map_model:
                    model_idx = self.val_map_model[self.pairs[idx][self.field_for_model_num]]
                    self.stochasticGraidentDescent(feature, target, model_idx)
                    finished_num += 1
                if (finished_num) % 1000 == 0:
                    sys.stdout.write("\rFINISHED PAIR NUM: %d...................................." % (finished_num+1))
                    sys.stdout.flush()
            loglikelihood = self.calLikelihood()
            sys.stdout.write("### Iteration: %d, current log likelihood: %f ###\n" % (ii+1, loglikelihood))
            sys.stdout.flush()
            if np.abs(loglikelihood-last_loglikelihood) < self.tol:
                break
            else:
                last_loglikelihood = loglikelihood
        print '\nFinishing learning Mean Regularized Multi-task Learing Model'


    def predict_proba(self, pairs, features):
        #features = np.array([feature+[1] for feature in features])
        features = np.array([feature for feature in features])
        probs = [0.0 for i in xrange(len(features))]
        for i in xrange(len(features)):
            feature = features[i]
            if pairs[i][self.field_for_model_num] not in self.val_map_model:
                lr_val = logisticVal(self.global_para, feature)
            else:
                model_idx = self.val_map_model[pairs[i][self.field_for_model_num]]
                lr_val = logisticVal(self.model_para[model_idx], feature)
            probs[i] = lr_val
        return probs


    def predict(self, pairs, features):
        #features = np.array([feature+[1] for feature in features])
        features = np.array([feature for feature in features])
        targets = [0 for i in xrange(len(features))]
        for i in xrange(len(features)):
            feature = features[i]
            if pairs[i][self.field_for_model_num] not in self.val_map_model:
                lr_val = logisticVal(self.global_para, feature)
            else:
                model_idx = self.val_map_model[pairs[i][self.field_for_model_num]]
                lr_val = logisticVal(self.model_para[model_idx], feature)
            if lr_val > 0.5:
                targets[i] = 1
        return targets


    def createMultiModel(self):
        val_set=set([entry[self.field_for_model_num] for entry in self.pairs])
        self.model_num = len(val_set)
        self.val_map_model = {}
        for val in val_set:
            self.val_map_model[val] = len(self.val_map_model)
        self.feature_dim = len(self.features[0])
        self.model_para = np.array([self.para_init_method(self.feature_dim) for
            i in xrange(self.model_num)])


    def createMultiModel1(self):
        field_cnt = {}
        for pair in self.pairs:
            key = pair[self.field_for_model_num]
            if key not in field_cnt:
                field_cnt[key] = 1
            else:
                field_cnt[key] += 1

        self.val_map_model = {}
        for val in field_cnt:
            if field_cnt[val] >= self.confidence:
                self.val_map_model[val] = len(self.val_map_model)
        self.model_num = len(self.val_map_model)
        self.feature_dim = len(self.features[0])
        self.model_para = np.array([self.para_init_method(self.feature_dim) for
            i in xrange(self.model_num)])
        #print self.model_num
        #raw_input()


    def stochasticGraidentDescent(self, feature, target, model_idx):
        lr_val = logisticVal(self.model_para[model_idx], feature)
        self.model_para[model_idx] = self.model_para[model_idx]\
                + self.lr*(target*feature-lr_val*feature
                - self.C*self.model_para[model_idx]
                - self.eta*(self.model_para[model_idx]-self.global_para))


    def calLossVal(self):
        correct_num = 0
        for i in xrange(self.nInstance):
            feature = self.features[i]
            target = self.targets[i]
            if self.pairs[i][self.field_for_model_num] in self.val_map_model:
                model_idx = self.val_map_model[self.pairs[i][self.field_for_model_num]]
                lr_val = logisticVal(self.model_para[model_idx], feature)
                if np.abs(lr_val-0.5)*target>0:
                    correct_num += 1
        return 1-1.0*correct_num/self.nInstance


    def calLikelihood(self):
        #pred_prob = np.array([0.0 for i in xrange(self.nInstance)])
        loglikelihood = 0.0
        for i in xrange(self.nInstance):
            feature = self.features[i]
            target = self.targets[i]
            if self.pairs[i][self.field_for_model_num] in self.val_map_model:
                model_idx = self.val_map_model[self.pairs[i][self.field_for_model_num]]
                pred_prob = logisticVal(self.model_para[model_idx], feature)
                if target == 1:
                    loglikelihood += np.log(pred_prob)
                else:
                    loglikelihood += np.log(1-pred_prob)
        #loglikelihood = np.dot(np.log(pred_prob).reshape(1, self.nInstance), self.targets)\
        #        + np.dot(np.log(1-pred_prob).reshape(1, self.nInstance), 1-self.targets)
        return loglikelihood

