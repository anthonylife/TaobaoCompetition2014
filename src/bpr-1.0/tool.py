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
# Providing some useful functions to Pairwise learning            #
###################################################################

import random, math

def rZero(k):
    return [0.0 for i in range(k)]

def rGaussian(k):
    factor = [random.normalvariate(0, 0.01) for i in xrange(k)]
    for i in xrange(len(factor)):
        if factor[i] > 1:
            factor[i] = 1
        elif factor[i] < -1:
            factor[i] = -1
    return factor

def logisticLoss(pos_score, neg_score):
    return (1-1.0/(1+math.exp(-(pos_score-neg_score))))
