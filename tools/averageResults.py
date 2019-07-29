#!/bin/python3
'''
    Average [TASK].results.txt (jsonl) files
'''
import json

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('result_files', nargs='*')
args = parser.parse_args()

# Sum
result = {}
for path in args.result_files:
    with open(path,'r') as f:
        newLine = json.loads(f.readline())
        for k in newLine.keys():
            result[k] = result.get(k,0) + newLine[k]

# Average
for k in result.keys():
    result[k] /= len(args.result_files)
print(result)
