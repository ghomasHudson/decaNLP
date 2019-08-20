#!/bin/python3
'''
    Print metric for each question
'''
import os
import json

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('result_dir')
parser.add_argument('data_dir')
parser.add_argument('--task_name')
parser.add_argument('--metric')
args = parser.parse_args()

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
    "MULTINLI": "em",
    "SRL": "nf1"
}

orig_prompts = {
    "multinli": 'Hypothesis: "{sent}" -- entailment, neutral, or contradiction?',
    "sst": 'Is this review negative or positive?',
    "iwslt": 'Translate from {source} to {target}.',
    "woz": 'What is the change in state?',
    "schema": '{mainQuestion} {choice1} or {choice2}?',
    "cnn": 'What is the summary?',
    "dailymail": 'What is the summary?',
    "wikisql": 'What is the translation from English to SQL?'
    }

def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def sigfig(num):
    return '%s' % float('%.3f' % num)

from pathlib import Path
pathlist = Path(args.result_dir).glob("*.results.txt")
for path in pathlist:
    res = json.loads(open(path,'r').readline())
    taskName = str(path.stem).split(".")[0]
    taskBase = ''.join(i for i in taskName.lower() if not i.isdigit())
    question = json.loads(open(os.path.join(args.data_dir,taskName,"val.jsonl"),'r').readline())["question"]
    metric=part_to_metric[taskBase.upper()]
    dist = levenshteinDistance(question,orig_prompts[taskBase])
    print(sigfig(dist),"\t",sigfig(res[metric]),"\t",question)
    # print(sigfig(res[args.metric])+","+sigfig(dist))
