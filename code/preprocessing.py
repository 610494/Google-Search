import os
import json
import string
import math
from tqdm import tqdm
from collections import OrderedDict


def dealEnglishData(datasetPath, outPath):
    questionVecs = []
    with open(datasetPath, 'r', encoding="utf-8") as dataset:
        jsonObj = dataset.read()
        parseJson = json.loads(jsonObj,  object_pairs_hook=OrderedDict)
        for paragraphID in parseJson:
            questionEnglishDict = {}
            paragraphSplitList = parseJson[paragraphID]["content"].split(' ')
            for paragraphSplit in paragraphSplitList:
                if len(paragraphSplit) == 0:
                    continue
                if paragraphSplit in questionEnglishDict:
                    questionEnglishDict[paragraphSplit] += 1
                else:
                    questionEnglishDict[paragraphSplit] = 0
            questionVecs.append(questionEnglishDict)
    print("Cutting...")

    questionWordDict = {}
    for wordDict in tqdm(questionVecs):
        for word in wordDict:
            questionWordDict[word] = questionWordDict.get(word, 0) + 1

    print("Counting...")

    QuestionNum = len(questionVecs)
    for vec in tqdm(questionVecs):
        for w in vec:
            vec[w] = vec[w] * \
                math.log10((QuestionNum + 1) / questionWordDict[w])

    print("Writting...")

    with open(outPath, "w", encoding="utf-8") as outfile:
        for dictionary in tqdm(questionVecs):
            json.dump(dictionary, outfile, ensure_ascii=False)
            outfile.write('\n')
