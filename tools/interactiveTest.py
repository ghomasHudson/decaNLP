'''Interactivly ask questions and visualise reponse'''

from pprint import pformat
import numpy as np
import random
import torch
import json
import os
#Import from parent dir
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import predict
import models

#****************************************************
# Functions
def addArg(argName,val=None):
    sys.argv.append("--"+argName)
    if val != None:
        sys.argv.append(val)
def boldString(s):
    '''Return the string, s in bold'''
    return'\033[1m\033[4m'+s+'\033[0m'

def colorBackground(s,colorCode):
    '''Return the string,s with th bg color'''
    return u"\u001b[48;5;"+str(colorCode)+'m'+s+"\033[0m"

def colorString(s,colorCode):
    '''Return the string, s in the color'''
    
    return f'\033[{colorCode}m{s}\033[0m' # Start to write colorized.

def printAttention(words,attentionVals):
    wordsStr = ""
    valStr = ""
    for i in range(len(attentionVals)):
        col = colorTransfer(attentionVals[i])
        wordTemp = "  "+words[i][:]+"  "
        wordsStr += colorBackground(wordTemp,col)
        formatStr = '{:>'+str(len(wordTemp))+'.2}'
        valStr += formatStr.format(attentionVals[i])
    print(wordsStr)
    print(valStr)

def colorTransfer(val):
    """Convert 0-1 into a grayscale terminal color code"""
    minCol = 235
    maxCol = 256
    return int((maxCol-minCol)*val + minCol)


def plotHist(data,xLabels,yLabels):
    maxXLabelsLength = max([len(x) for x in xLabels])+1
    #maxYLabelsLength = max([len(yLabels)])
    print(" "+" "*maxXLabelsLength + "  ".join(yLabels))
    for i in range(len(xLabels)):
        row = str('{:>'+str(maxXLabelsLength)+'}').format(xLabels[i])+" "
        for col in range(len(yLabels)):
            val = data[col][i]
            blockLength = len(yLabels[col])+1
            valFormat = " "+str("{:<"+str(blockLength)+".2f}").format(val)
            row += colorBackground(valFormat,colorTransfer(val))#*blockLength
        print(row)








#***************************************************
# Main code
addArg("tasks",".temp")
addArg("overwrite")

print(sys.argv)
args = predict.get_args()
print(f'Arguments:\n{pformat(vars(args))}')

#Set random seeds
np.random.seed(args.seed)
random.seed(args.seed)
torch.manual_seed(args.seed)
torch.cuda.manual_seed(args.seed)

#Setup the model
print(f'Loading from {args.best_checkpoint}')
save_dict = torch.load(args.best_checkpoint)
field = save_dict['field']
print(f'Initializing Model')
Model = getattr(models, args.model) 
model = Model(field, args)
model_dict = save_dict['model_state_dict']
backwards_compatible_cove_dict = {}
for k, v in model_dict.items():
    if 'cove.rnn.' in k:
        k = k.replace('cove.rnn.', 'cove.rnn1.')
    backwards_compatible_cove_dict[k] = v
model_dict = backwards_compatible_cove_dict
model.load_state_dict(model_dict)

while True:
    try:
        import shutil
        shutil.rmtree("../.data/.temp")
    except:
        pass
    #Get input
    question = input("question: ")
    context = input("context: ")

    #question = "Is the sentence -- positive or negative?"
    #context = "I really love this movie!"
    if question == "" or context == "":
        print("Blank... Exiting")
        import sys
        sys.exit()

    taskDir = os.path.join(args.data,".temp")
    try:
        os.makedirs(taskDir)
    except:
        print("temp exists")
    with open(os.path.join(taskDir,"val.jsonl"),'w') as f:
        json.dump({"question":question,"context":context,"answer":""},f)



    #Load data
    field, splits = predict.prepare_data(args, field)
    model.set_embeddings(field.vocab.vectors)
    device = predict.set_seed(args)
    print(f'Preparing iterators')
    if len(args.val_batch_size) == 1 and len(val_sets) > 1:
        args.val_batch_size *= len(val_sets)

    val_sets = splits
    iters = [(name, predict.to_iter(x, bs, device)) for name, x, bs in zip(args.tasks, val_sets, args.val_batch_size)]

    def mult(ps):
        r = 0
        for p in ps:
            this_r = 1
            for s in p.size():
                this_r *= s
            r += this_r
        return r
    params = list(filter(lambda p: p.requires_grad, model.parameters()))
    num_param = mult(params)
    print(f'{args.model} has {num_param:,} parameters')
    model.to(device)

    #Predict
    decaScore = []
    model.eval()
    with torch.no_grad():
        for task, it in iters:
            print(task)
            predictions = []
            ids = []
            for batch_idx, batch in enumerate(it):
                _, p,attentions = model(batch)

                p = field.reverse(p)
                answer = p[0]

    questionTokenized = ["<START>"]+field.preprocess(question)+["<END>"]
    contextTokenized = ["<START>"]+field.preprocess(context)+["<END>"]
    answerTokenized = field.preprocess(answer)+["<END>"]

    print("-----")
    print(boldString("answer"))
    print(answer)

    #Calculate probabilities
    vocabProbs = attentions["vocab_pointer"].squeeze()
    context_question_ptrs = attentions["context_question_pointer"].squeeze()
    questionProbs = (1-context_question_ptrs) * (1-vocabProbs)
    contextProbs = (context_question_ptrs) * (1-vocabProbs)

    vocabProbs = vocabProbs.tolist()
    questionProbs = questionProbs.tolist()
    contextProbs = contextProbs.tolist()

    # Plot answer coloured with pointer source (vocab/context/question)
    # - vocab
    
    print(boldString("Pointers"))
    plotHist(np.transpose([vocabProbs,questionProbs,contextProbs]),["p(vocab)","p(question)","p(context)"],answerTokenized)

    print(boldString("Max pointer"))
    maxPtrs = np.argmax((vocabProbs,questionProbs,contextProbs),0)
    for i in range(len(answerTokenized)):
        print(colorString(answerTokenized[i],[94,91,96][maxPtrs[i]]),end="\033[0m")
    print()

    '''
    for prob in [(vocabProbs,"p(vocab)"),(questionProbs,"p(question)"),(contextProbs,"p(context)")]:
        print(boldString(prob[1]))
        printAttention(answerTokenized,prob[0])
    '''
    #Plot summary of pointer
    from plotPointers import plot
    plot(np.average((vocabProbs,questionProbs,contextProbs),1),["vocab","question","context"],title="Pointer Summary")



    #Plot histogram of answer-context attention
    print(boldString("Context-answer attention"))

    context_attn = attentions["context_attention"].squeeze().tolist()
    plotHist(context_attn,contextTokenized,answerTokenized)

    print(boldString("Question-answer attention"))
    question_attn = attentions["question_attention"].squeeze().tolist()
    plotHist(question_attn,questionTokenized,answerTokenized)



