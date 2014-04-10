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
# Call Mean Regularized Multi-task Learning with LR model         #
###################################################################

import csv, json, sys, argparse
sys.path.append("../")
import data_io
from multiTaskLR import MeanRegularizedMultiTaskLR

settings = json.loads(open("../../SETTINGS.json").read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=int, action='store',
            dest='target', help='for validation or test dataset')

    if len(sys.argv) != 3:
        print 'Command e.g.: python train.py -t 0(1)'
        sys.exit(1)

    para = parser.parse_args()
    if para.target == 0:
        features_targets = [entry for entry in csv.reader(open(settings["MTLR_TRAIN_FILE"]))]
    elif para.target == 1:
        features_targets = [entry for entry in csv.reader(open(settings["MTLR_TRAIN_FILE_FOR_SUBMIT"]))]
    else:
        print 'Invalid train data target choice...'
        sys.exit(1)
    features = [map(float, entry[2:-1]) for entry in features_targets]
    pairs = [map(int, entry[:2]) for entry in features_targets]
    targets = [map(int, entry[-1]) for entry in features_targets]

    classifier = MeanRegularizedMultiTaskLR(C=1,
                                    tol=0.0001,
                                    intercept_scaling=1,
                                    lr=0.01,
                                    eta=1,
                                    field_for_model_num=2,
                                    max_niters=500,
                                    para_init="gaussian")
    classifier.fit(pairs, features, targets)
    data_io.save_model(classifier, settings["MTLR_MODEL_FILE"])


if __name__ == "__main__":
    main()
