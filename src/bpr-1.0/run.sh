#!/bin/sh

# Use multiple user behavior
#python train.py -Retrain True -Init gaussian -Csampling uniform -Cbehavior triple -topk 4
#python train.py -Retrain False -Init gaussian -Csampling uniform -Cbehavior triple -topk 2

# Use single user behavior
#python train.py -Retrain True -Init gaussian -Csampling uniform -Cbehavior tuple -topk 4
python train.py -Retrain False -Init gaussian -Csampling uniform -Cbehavior tuple -topk 3

#python train.py -Retrain True -Init zero(gaussian) -Csampling uniform(pairwise/listwise) -Cbehavior single(various) -topk 4

