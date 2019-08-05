#!/bin/python3
'''
    Average [TASK].results.txt (jsonl) files
'''
import json
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('result_directory',type=str,help="Directory containing the .results.txt files")
parser.add_argument('--test_ids', type=argparse.FileType('r'),help="File containing question IDs (e.g. WIKISQL0), one per line. \nThis specifies the test set.")
args = parser.parse_args()

# Load test set ids from file
if args.test_ids:
    ids = args.test_ids.readlines()
    ids = [i.replace("\n","") for i in ids]
else:
    ids = []

part_to_metric = {
    "CNN": "avg_rouge",
    "DAILYMAIL": "avg_rouge",
    "IWSLT": "bleu",
    "SST": "em",
    "WIKISQL": "lfem",
    "WOZ": "joint_goal_em",
    "SCHEMA": "em",
    "ZRE": "corpus_f1",
    "SQUAD": "nf1",
    "NLI": "em",
    "SRL": "nf1"
}

# Count
# Sum
result = {}
counts = {}
directory = os.fsencode(args.result_directory)
files = list(os.listdir(directory))
for f in files:
    filename = os.fsdecode(f)
    if filename.endswith(".results.txt"):
        task = filename.split(".")[0]
        task = ''.join(filter(str.isalpha,task))

        #check if in test set
        if len(ids) > 0 and filename.split(".")[0] not in ids:
            continue

        # Init data
        if task not in result.keys():
            result[task] = {}
            counts[task] = 0

        counts[task] += 1
        path = os.path.join(args.result_directory, filename)
        with open(path,'r') as f:
            newLine = json.loads(f.readline())
            for k in newLine.keys():
                result[task][k] = result[task].get(k,0) + newLine[k]
        continue
    else:
     continue

# Average
for task in result.keys():
    for k in result[task].keys():
        result[task][k] /= counts[task]

print()
for task in result.keys():
    for k in part_to_metric.keys():
        if k in task:
            print( '{:>20}'.format(task),"|",result[task][part_to_metric[k]])
            break
