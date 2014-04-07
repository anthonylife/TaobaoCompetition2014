#!/bin/sh

python makeFeature.py -t 0
#python makeFeature.py -t 1

python cluster.py -t 0 -c1 20 -c2 50
#python cluster.py -t 1 -c1 20 -c2 50

python predict.py -t 0 -c1 20 -c2 50
#python predict.py -t 1 -c1 20 -c2 50
