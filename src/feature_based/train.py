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
# Date: 2014/4/1                                                  #
# Gradient Boosting Decision/Regression Tree-based Method         #
###################################################################

import csv, json, sys, argparse
sys.path.append("../")
import data_io
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor

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
        features_targets = [entry for entry in csv.reader(open(settings["GBT_TRAIN_FILE"]))]
    elif para.target == 1:
        features_targets = [entry for entry in csv.reader(open(settings["GBT_TRAIN_FILE_FOR_SUBMIT"]))]
    else:
        print 'Invalid train data target choice...'
        sys.exit(1)
    features = [map(float, entry[2:-1]) for entry in features_targets]
    targets = [map(int, entry[-1]) for entry in features_targets]

    classifier = RandomForestClassifier(n_estimators=50,
                                        verbose=2,
                                        n_jobs=1,
                                        min_samples_split=10,
                                        random_state=1)
    classifier.fit(features, targets)
    data_io.save_model(classifier, settings["GBT_MODEL_FILE"])


if __name__ == "__main__":
    main()
