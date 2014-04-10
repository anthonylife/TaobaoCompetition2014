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
# Call model.py to do time-aware multi-beahvior matrix            #
#   factorization                                                 #
###################################################################

import sys, csv, json, argparse
sys.path.append("../")
from data_io import write_submission
from model import MBTALMF

settings = json.loads(open("../../SETTINGS.json").read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-init', type=str, action='store', dest='init_choice',
            help='specify which method to initialize model parameters')
    parser.add_argument('-retrain', type=str, action='store',dest='retrain_choice',
            help='specify which method to initialize model parameters')
    parser.add_argument('-tv', type=float, action='store', dest='threshold_val',
            help='specify the threshold value to generate recommendations')
    parser.add_argument('-t', type=int, action='store',
            dest='target', help='for validation or test dataset')

    if len(sys.argv) != 9:
        print 'Command e.g.: python train.py -retrain True -init zero(gaussian) '\
                + '-tv 0.8 -t 0(1)'
    para = parser.parse_args()
    mbtalmf = MBTALMF()

    if para.target == 0:
        data_file = settings["TRAIN_DATA_FILE"]
    elif para.target == 1:
        data_file = settings["TAR_DATA_FILE"]
    else:
        print 'Choice of file invalid!'
        sys.exit(1)

    if para.retrain_choice == "True":
        mbtalmf.model_init(data_file, para.init_choice, para.target)
        mbtalmf.train()
        recommend_result = mbtalmf.genRecommendResult(True, data_file,
                para.init_choice, para.threshold_val, para.target)
        write_submission(recommend_result)
    else:
        recommend_result = mbtalmf.genRecommendResult(False, data_file,
                para.init_choice, para.threshold_val, para.target)
        write_submission(recommend_result)


if __name__ == "__main__":
    main()

