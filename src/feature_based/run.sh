#!/bin/sh

python genPairs.py -t 0 -r 5
#python genPairs.py -t 1 -r 5
python genPairs.py -t 2 -r 5
#python genPairs.py -t 3 -r 5
echo 'Finish generating pairs'

python makeFeature.py -d 0
#python makeFeature.py -d 1
python makeFeature.py -d 2
#python makeFeature.py -d 3
echo ''
echo 'Finish generating features'

python train.py -t 0 >/dev/null 2>&1
#python train.py -t 1 >/dev/null 2>&1

python predict.py -tv 0.9 -t 0 >/dev/null 2>&1
#python predict.py -tv 0.8 -t 1 >/dev/null 2>&1
