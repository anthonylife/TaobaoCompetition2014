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
# Call model.py to do weighted matrix factorization               #
###################################################################
import sys, csv, json, argparse
sys.path.append("../")
from data_io import write_submission
from model import WMF

settings = json.loads(open("../../SETTINGS.json").read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-init', type=str, action='store', dest='init_choice',
            help='specify which method to initialize model parameters')
    parser.add_argument('-retrain', type=str, action='store',dest='retrain_choice',
            help='specify which method to initialize model parameters')
    parser.add_argument('-tv', type=float, action='store', dest='threshold_val',
            help='specify the threshold value to generate recommendations')

    if len(sys.argv) != 7:
        print 'Command e.g.: python train.py -retrain True -init zero(gaussian) '\
                + '-tv 0.8'
        sys.exit(1)

    para = parser.parse_args()
    wmf = WMF()
    if para.retrain_choice == "True":
        wmf.model_init(settings["WMF_LR_ALS"], settings["TRAIN_DATA_FILE"], para.init_choice)
        wmf.train(settings["WMF_LR_ALS"])
        recommend_result = wmf.genRecommendResult(True, settings["WMF_LR_ALS"], settings["TRAIN_DATA_FILE"], para.init_choice, para.threshold_val)
        write_submission(recommend_result)
    else:
        recommend_result = wmf.genRecommendResult(False, settings["WMF_LR_ALS"], settings["TRAIN_DATA_FILE"], para.init_choice, para.threshold_val)
        write_submission(recommend_result)

if __name__ == "__main__":
    main()
