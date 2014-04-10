#!/bin/sh

#python cleanData.py -t 0 -d 5
#python cleanData.py -t 1 -d 5
#python cleanData.py -t 0 -d 5
#python cleanData.py -t 1 -d 5
echo 'Finish cleaning data'


python genPairs.py -t 0 -r 5 -c 0
#python genPairs.py -t 1 -r 5 -c 0
python genPairs.py -t 2 -r 5 -c 0
#python genPairs.py -t 3 -r 5 -c 0

#python genPairs.py -t 0 -r 5 -c 1
#python genPairs.py -t 1 -r 5 -c 1
#python genPairs.py -t 2 -r 5 -c 1
#python genPairs.py -t 3 -r 5 -c 1
echo 'Finish generating pairs'


python makeFeature.py -d 0 -tv 2.5
#python makeFeature.py -d 1 -tv 2.0
python makeFeature.py -d 2 -tv 2.5
#python makeFeature.py -d 3 -tv 2.0
#python makeFeature1.py -d 0
#python makeFeature1.py -d 1
#python makeFeature1.py -d 2
#python makeFeature1.py -d 3
echo ''
echo 'Finish generating features'


python train.py -t 0 
#python train.py -t 0 >/dev/null 2>&1
#python train.py -t 1 
#python train.py -t 1 >/dev/null 2>&1


python predict.py -tv 0.99 -t 0
#python predict.py -tv 0.99 -t 0 >/dev/null 2>&1
#python predict.py -tv 0.968 -t 1
#python predict.py -tv 0.999 -t 1 >/dev/null 2>&1
