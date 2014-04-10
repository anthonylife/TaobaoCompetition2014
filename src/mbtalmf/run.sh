#!/bin/sh

python train.py -retrain True -init gaussian -tv 0.8 -t 0
#python train.py -retrain False -init gaussian -tv 0.9 -t 0

#python train.py -retrain True -init gaussian -tv 0.8 -t 1
#python train.py -retrain False -init gaussian -tv 0.9 -t 1

