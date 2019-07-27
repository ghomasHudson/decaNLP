#
'''Plot question/context/vocab pointer distribution'''

import glob
import argparse
import os
import numpy as np

def loadPointers(f):
    """Load pointer values from file"""
    output = []
    for l in f.readlines():
        ls = l[:-1].split(",")
        output.append(np.array([float(a) for a in ls]))
    return output

import sys


TICK = '▇'
SM_TICK = '▏'

def plot(data,labels,title=""):
    maxWidth = 50
    color = [94,91,96]
    maxLabelLength = max([len(x) for x in labels])

    print('\033[1m\033[4m'+title+'\033[0m')

    for i,row in enumerate(data):
        formatStr = '{:>'+str(maxLabelLength)+'}'
        sys.stdout.write(formatStr.format(labels[i])+" ")
        sys.stdout.write(f'\033[{color[i]}m') # Start to write colorized.
        numBlocks = int(row*maxWidth)
        if numBlocks == 0:
            sys.stdout.write(SM_TICK)
        for _ in range(numBlocks):
            sys.stdout.write(TICK)
        sys.stdout.write('\033[0m') # Back to original.
        sys.stdout.write(' '+"{:.2f}".format(row))
        print()

def pointerToProbs(vocabPtr,questionContextPtr):
    '''Convert pointers to probaiblities'''
    questionProb = questionContextPtr * (1-vocabPtr)
    contextProb = (1-questionContextPtr) * (1-vocabPtr)
    return vocabPtr, questionProb, contextProb

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot question/context/vocab pointer distribution.')
    parser.add_argument('--inputDir', metavar='I',
                        help='directory where the pointer outputs are saved',required=True)

    args = parser.parse_args()



    vocab_ptr_files = sorted([f for f in glob.glob(os.path.join(args.inputDir,"*.vocab_pointer.txt"))])
    for f in vocab_ptr_files:
        task = f[:-18].split("/")[-1] #get task name

        #Load pointer values
        context_question_filename = f[:-18]+".context_question_pointer.txt"
        with open(f,'r') as vocab_pointer_file:
            vocab_ptrs = loadPointers(vocab_pointer_file)
        with open(context_question_filename,'r') as context_question_pointer_file:
            question_context_ptrs = loadPointers(context_question_pointer_file)

        #Calculate average pointer values
        vocabProbs = []
        questionProbs = []
        contextProbs = []
        for lineIdx in range(len(vocab_ptrs)):
            for tokenIdx in range(len(vocab_ptrs[lineIdx])):
                lineProbs = pointerToProbs(vocab_ptrs[lineIdx][tokenIdx],question_context_ptrs[lineIdx][tokenIdx])
                vocabProbs.append(lineProbs[0])
                questionProbs.append(lineProbs[1])
                contextProbs.append(lineProbs[2])
        avgs = np.average((vocabProbs,questionProbs,contextProbs),1).tolist()
        
        #Plot the result
        plot(avgs,["vocab","question","context"],title=task)




