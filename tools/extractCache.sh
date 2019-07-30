#!/bin/sh
# Copy all the decanlp jsonl cache

if [ "$#" -ne 2 ] || ! [ -d "$1" ]; then
    echo "Usage: $0 DECANLP_DATA_DIR NEW_DIR"
    exit 1
fi


MoveTask () {
    #$1 new dir
    #$2 name of task (new)
    #$3 path of orig e.g $1/cnn-----------/.cache/None.jsonl
    mkdir $1/$2
    CopyAndFix $3 $1/$2/val.jsonl
}

CopyAndFix () {
    #$1 path of orig e.g $1/cnn-----------/.cache/None.jsonl
    #$2 path to copy to
    cp $1 $2
    sed -i 's/answerRaw/answer/' $2
    sed -i 's/questionRaw/question/' $2
    sed -i 's/contextRaw/context/' $2
}

mkdir $2

MoveTask $2 CNN $1/cnn/cnn/.cache/validation.jsonl/None.jsonl
MoveTask $2 DAILYMAIL $1/dailymail/dailymail/.cache/validation.jsonl/None.jsonl
MoveTask $2 IWSLT $1/iwslt/en-de/.cache/IWSLT16.TED.tst2013.en-de/20000000.jsonl
MoveTask $2 MULTINLI $1/multinli/multinli_1.0/.cache/validation.jsonl/None/multinli.in.out.jsonl
MoveTask $2 SCHEMA $1/schema/.cache/validation.jsonl/None.jsonl
MoveTask $2 SST $1/sst/.cache/dev_binary_sent.csv/None.jsonl
MoveTask $2 SRL $1/srl/.cache/dev.jsonl/None.jsonl
MoveTask $2 WIKISQL $1/wikisql/data/.cache/query_as_context/dev.jsonl/None.jsonl
MoveTask $2 WOZ $1/woz/.cache/validate.jsonl/None/woz.en.jsonl
MoveTask $2 ZRE $1/zre/relation_splits/.cache/dev.jsonl/None.jsonl
MoveTask $2 SQUAD $1/squad/.cache/dev-v1.1.json/None.jsonl
