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



import re
def natural_sorted(iterable, key=None, reverse=False):
    """Return a new naturally sorted list from the items in *iterable*.

    The returned list is in natural sort order. The string is ordered
    lexicographically (using the Unicode code point number to order individual
    characters), except that multi-digit numbers are ordered as a single
    character.

    Has two optional arguments which must be specified as keyword arguments.

    *key* specifies a function of one argument that is used to extract a
    comparison key from each list element: ``key=str.lower``.  The default value
    is ``None`` (compare the elements directly).

    *reverse* is a boolean value.  If set to ``True``, then the list elements are
    sorted as if each comparison were reversed.

    The :func:`natural_sorted` function is guaranteed to be stable. A sort is
    stable if it guarantees not to change the relative order of elements that
    compare equal --- this is helpful for sorting in multiple passes (for
    example, sort by department, then by salary grade).
    """
    prog = re.compile(r"(\d+)")

    def alphanum_key(element):
        """Split given key in list of strings and digits"""
        return [int(c) if c.isdigit() else c for c in prog.split(key(element)
                if key else element)]

    return sorted(iterable, key=alphanum_key, reverse=reverse)



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
    "MULTINLI": "em",
    "SRL": "nf1"
}

# Count
# Sum
result = {}
counts = {}
directory = os.fsencode(args.result_directory)
files = list(os.listdir(directory))
files = natural_sorted([os.fsdecode(s) for s in files])
for f in files:
    # filename = os.fsdecode(f)
    filename = f
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

            full_task_name = filename.split(".")[0].split("/")[-1]
            print(full_task_name,"\t",newLine[part_to_metric[task]])
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
