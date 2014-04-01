#!/bin/sh

#python genPairs.py -t 0 
#python genPairs.py -t 1
#python genPairs.py -t 2
#python genPairs.py -t 3
echo 'Finish generating pairs'

#python makeFeature.py -d 0
#python makeFeature.py -d 1
#python makeFeature.py -d 2
#python makeFeature.py -d 3
echo ''
echo 'Finish generating features'

#python train.py -t 0 >/dev/null 2>&1
#python train.py -t 1 >/dev/null 2>&1

#python predict.py -tv 0.5 -t 0
python predict.py -tv 0.5 -t 0 >/dev/null 2>&1
#python predict.py -tv 0.8 -t 1 >/dev/null 2>&1
