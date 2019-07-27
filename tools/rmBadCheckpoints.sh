#!/bin/bash
# Delete certain checkpoints
regex="$1/iteration_([0-9]+)(.pth|_rank_0_optim.pth)"
echo $regex
for filename in $1/*.pth; do
    if [[ $filename =~ $regex ]]; then
        echo $filename
        n="${BASH_REMATCH[1]}"
        #n=$(($n%10000)) # every 10,000
        n=$(($n%50000)) # every 50,000
        if [[ $n -ne 0 ]]; then
            echo "  del $filename"
            rm $filename
        fi
    fi
done

