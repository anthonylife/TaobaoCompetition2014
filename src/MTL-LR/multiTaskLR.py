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

import sys, json, random
sys.path.append("../")
import numpy as np
from tool import rZero, rGaussian, logisticVal

settings = json.loads(open("../../SETTINGS.json").read())


class MeanRegularizedMultiTaskLR():
    def __init__(self, C=1, tol=0.0001, intercept_scaling=1, lr = 0.01, eta=1,
            field_for_model_num=1, max_niters = 500, para_init="gaussian"):
        self.C = C
        self.tol = tol
        self.intercept = intercept_scaling
        self.lr = lr
        self.eta = eta
        self.field_for_model_num = field_for_model_num-1
        self.max_niters = max_niters
        if para_init == settings["MTLR_INIT_GAUSSIAN"]:
            self.para_init_method = rGaussian
        elif para_init == settings["MTLR_INIT_ZERO"]:
            self.para_init_method = rZero
        else:
            print 'Invalid method choice of parameter initialization'
            sys.exit(1)


    def fit(self, features, targets):
        self.features = [feature+[1] for feature in features]
        if not np.all(targets>-1):
            print 'Data label = -1 or = 1'
            sys.exit(1)
        self.targets = targets

        if len(self.features) != len(self.targets):
            print 'Mismatch for number of features and number of targets'
            sys.exit(1)
        self.nInstance = len(self.targets)
        self.createMultiModel()

        visit_idxs = [i for i in xrange(self.nInstance)]
        last_lossval = 0.0
        for ii in xrange(self.max_niters):
            random.shuffle(visit_idxs)
            for idx in visit_idxs:
                feature = self.features[idx]
                target = self.targets[idx]
                model_idx = self.val_map_model[feature[self.field_for_model_num]]
                self.stochasticGraidentDescent(feature, target, model_idx)
            cur_lossval = self.calLossVal()
            sys.stdout.write("\r### Iteration: %d, current loss value: %f ###" % (ii+1, cur_lossval))
            sys.stdout.flush()
            if np.abs(cur_lossval-last_lossval) < self.tol or cur_lossval < self.tol:
                break
        print '\nFinishing learning Mean Regularized Multi-task Learing Model'


    def predict_prob(self, features):
        features = [feature+[1] for feature in features]
        probs = [0.0 for i in xrange(len(features))]
        for i in xrange(len(features)):
            feature = features[i]
            if feature[self.field_for_model_num] not in self.val_map_model:
                print 'Cannot map the feature instance to any existing single LR model'
                sys.exit(1)
            model_idx = self.val_map_model[feature[self.field_for_model_num]]
            lr_val = logisticVal(self.model_para[model_idx], feature)
            probs[i] = lr_val
        return probs


    def predict(self, features):
        features = [feature+[1] for feature in features]
        targets = [0 for i in xrange(len(features))]
        for i in xrange(len(features)):
            feature = features[i]
            if feature[self.field_for_model_num] not in self.val_map_model:
                print 'Cannot map the feature instance to any existing single LR model'
                sys.exit(1)
            model_idx = self.val_map_model[feature[self.field_for_model_num]]
            lr_val = logisticVal(self.model_para[model_idx], feature)
            if lr_val > 0.5:
                targets[i] = 1
        return targets


    def createMultiModel(self):
        val_set=set([entry[self.field_for_model_num] for entry in self.features])
        self.model_num = len(val_set)
        self.val_map_model = {}
        for val in val_set:
            self.val_map_model[val] = len(self.val_map_model)
        self.feature_num = len(self.features[0])
        self.model_para = np.array([self.para_init_method(self.feature_num) for
            i in xrange(self.model_num)])


    def stochasticGraidentDescent(self, feature, target, model_idx):
        lr_val = logisticVal(self.model_para[model_idx], feature)
        avg_model_para = np.mean(self.model_para, 0)
        self.model_para[model_idx] = self.model_para[model_idx]\
                + self.lr*(target*feature-lr_val*self.model_para[model_idx]
                - self.C*self.model_para[model_idx]
                - self.eta*(self.model_para[model_idx]-avg_model_para))


    def calLossVal(self):
        correct_num = 0
        for i in xrange(self.nInstance):
            feature = self.features[i]
            target = self.targets[i]
            model_idx = self.val_map_model[feature[self.field_for_model_num]]
            lr_val = logisticVal(self.model_para[model_idx], feature)
            if np.abs(lr_val-0.5)*target>0:
                correct_num += 1
        return 1-1.0*correct_num/self.nInstance

