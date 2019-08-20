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
    '''Plot in terminal

    data: dictionary of values

    '''
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

'''
def plot(data):
    """Plot in matplotlib"""
    import matplotlib.pyplot as plt
    import numpy as np
    print(data)
    COLORS = ["b","r","g"]

    #Reflect data
    dataSeries = {}
    for task in data:
        for pointer in data[task]:
            dataSeries[pointer] = dataSeries.get(pointer,[]) + [data[task][pointer]]

    fig, ax = plt.subplots(figsize=(6,3))
    start=0
    bar_width=0.15
    index = np.arange(len(list(dataSeries.values())[0]))
    for i,pointer in enumerate(dataSeries):
        plt.bar(index+i*(bar_width),dataSeries[pointer],bar_width,label=pointer,color=COLORS[i])
    plt.xticks(index + bar_width,data.keys())
    #plt.ylim(0,1)
    plt.yticks([0,0.5,1])
    ax.tick_params(direction="inout")
    #plt.tight_layout()
    plt.show()
'''

def pointerToProbs(vocabPtr,questionContextPtr):
    '''Convert pointers to probaiblities'''
    contextProb = questionContextPtr * (1-vocabPtr)
    questionProb = (1-questionContextPtr) * (1-vocabPtr)

    return vocabPtr, questionProb, contextProb

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot question/context/vocab pointer distribution.')
    parser.add_argument('inputDir', metavar='I',
                        help='directory where the pointer outputs are saved')
    parser.add_argument('--seperate',action="store_true",
                        help='Dont combine tasks')
    args = parser.parse_args()



    vocab_ptr_files = sorted([f for f in glob.glob(os.path.join(args.inputDir,"*.vocab_pointer.txt"))])
    data = {}
    for f in vocab_ptr_files:
        task = f[:-18].split("/")[-1] #get task name
        task = task.split(".")[0]

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
            vp = []
            qp = []
            cp = []
            for tokenIdx in range(len(vocab_ptrs[lineIdx])):
                lineProbs = pointerToProbs(vocab_ptrs[lineIdx][tokenIdx],question_context_ptrs[lineIdx][tokenIdx])


                #Convert to max (1 for biggest, 0 otherwise)
                a = np.argmax(lineProbs)
                lineProbs = [0,0,0]
                lineProbs[a] = 1

                vocabProbs.append(lineProbs[0])
                questionProbs.append(lineProbs[1])
                contextProbs.append(lineProbs[2])

        avgs = np.average((vocabProbs,contextProbs,questionProbs),1).tolist()
        print(task,"\t","\t".join([str(a) for a in avgs]))

        #Plot the result
        #plot(avgs,["vocab","context","question"],title=task)
        #data[task] = {"vocab":avgs[0],"context":avgs[1],"question":avgs[2]}

    #plot(data)




