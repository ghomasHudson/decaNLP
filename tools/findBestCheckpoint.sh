#!/bin/bash
# Runs decanlp predict on every checkpoint in a folder
#   arg1: path of checkpoint folders
#   All other args are passed to the command

if [ "$#" -lt 1 ]; then
    echo "Incorrect number of parameters"
    echo ""
    echo "Usage:"
    echo "  $0 CHECKPOINT_PATH [decanlp parameters...]"
    echo
    exit
fi

# Clear existing output
sumsName=$1"/checkpointSums.txt"
scoresName=$1"/checkpointScores.txt"
echo -n "" > $sumsName
echo -n "" > $scoresName

for f in $(ls -v -1 $1/*[0-9].pth) # loop in numerical order
do
    echo ""
    echo ""
    echo "**********************************************************"
    echo "  Evaluating $f"
    echo "**********************************************************"

    # Check if we've already done the evaluation
    if [ ! -f "$1/$(basename -s .pth $f)/valid_find_checkpoint/iwslt.en.de.results.txt" ]; then
        echo "  Evaluating..."
        python predict.py "${@:2}" --path $1 --checkpoint_name `basename $f`  --evaluate valid_find_checkpoint --tasks squad iwslt.en.de multinli.in.out sst srl zre woz.en wikisql schema
    else
        echo "Using existing result..."
    fi

    #Get the results
    RESULTS[0]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/iwslt.en.de.results.txt" | jq '.bleu'`
    RESULTS[1]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/multinli.in.out.results.txt" | jq '.em'`
    RESULTS[2]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/schema.results.txt" | jq '.em'`
    RESULTS[3]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/squad.results.txt" | jq '.nf1'`
    RESULTS[4]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/srl.results.txt" | jq '.nf1'`
    RESULTS[5]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/sst.results.txt" | jq '.em'`
    RESULTS[6]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/wikisql.results.txt" | jq '.lfem'`
    RESULTS[7]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/woz.en.results.txt" | jq '.joint_goal_em'`
    RESULTS[8]=`cat "$1/$(basename -s .pth $f)/valid_find_checkpoint/zre.results.txt" | jq '.corpus_f1'`

    #Output
    sum=`printf "%f\n" "${RESULTS[@]}" | sort -nr | awk 'NR>1 && p!=$0{print x;exit;}{x+=$0;p=$0;}'`
    file=`basename $f`
    iteration="${file//[!0-9]/}"
    echo "$iteration $sum" >> $sumsName
    echo "${file//[!0-9]/} ${RESULTS[*]}" >> $scoresName
done

echo
echo
echo "Individual scores saved to '$scoresName'"
echo "Summed scores saved to '$sumsName'"
