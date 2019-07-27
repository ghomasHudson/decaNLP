#!/bin/bash
#Script to run paraphrase evaluations on all questions
# - cmdline params are still passed to script
# - this code only handles filling the --tasks param

#Exit if something errors
set -e

dataDir=".data2"
echo "Loading data from $dataDir"

countFileWithName() {
    a=`ls -dq $dataDir/$1* | wc -l`
    let b=$a-1
    echo $b
}

repeat () {
    seq -s " " -f "$1%g" 0 `countFileWithName $1`
}

#python predict.py $@ --data $dataDir --tasks `repeat "IWSLT"` --bleu
#python predict.py $@ --data $dataDir --tasks `repeat "CNN"` --rouge
python predict.py $@ --data $dataDir --tasks `repeat "DAILYMAIL"` --rouge
python predict.py $@ --data $dataDir --tasks `repeat "MULTINLI"`
python predict.py $@ --data $dataDir --tasks `repeat "SST"`
python predict.py $@ --data $dataDir --tasks `repeat "WOZ"` --joint_goal_em
python predict.py $@ --data $dataDir --tasks `repeat "WIKISQL"` --logical_form
python predict.py $@ --data $dataDir --tasks `repeat "SCHEMA"`

