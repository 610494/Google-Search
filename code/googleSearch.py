from parserSearchResult import GetParagraphFromLinks
from googleAPI import Search
from collections import OrderedDict
import json
import os
from preprocessing import dealEnglishData
from faq import tfidf
import math


def GetParagraphList(question):
    question = question.replace('"', "'")
    current_dir = os.path.dirname(__file__)

    TruthfulListPath = os.path.join(
        current_dir, '..', 'data', 'TruthfulQAQuestionList.json')
    TruthfulPagaPath = os.path.join(
        current_dir, '..', 'data', 'TruthfulQAGoogleSearchResult.json')
    # TruthfulListPath = "../data/TruthfulQAQuestionList.json"
    # TruthfulPagaPath = "../data/TruthfulQAGoogleSearchResult.json"
    MAXToken = 150

    with open(TruthfulListPath) as f:
        questionJsonList = json.load(f,  object_pairs_hook=OrderedDict)
        for oneJsonQuestion in questionJsonList:
            if question[:-1] == questionJsonList[oneJsonQuestion][:-1]:
                retList = []
                with open(TruthfulPagaPath, "r") as f:
                    TruthfulQPJsonList = json.load(f)["searchResult"]
                    for i in TruthfulQPJsonList:
                        if question == i["query"] or question[:-1] == i["query"]:
                            for j in i["paragraph"]:
                                oneParagraph = j.replace("\r", " ").replace(
                                    "\n", " ").replace("\t", " ")
                                for i in range(math.floor(len(oneParagraph) / MAXToken)):
                                    retList.append(
                                        oneParagraph[i*MAXToken:((i+1)*MAXToken)])
                                retList.append(
                                    oneParagraph[(math.floor(len(oneParagraph) / MAXToken)) * MAXToken:])
                # theMaxNum = 0
                # for i in retList:
                #     theMaxNum = max(theMaxNum, len(i))
                # print("max token number: ", theMaxNum)
                return retList
    SearchLink = Search(question)
    # print("network")
    return GetParagraphFromLinks(SearchLink)


def GetParagraph(question, k):
    paragraphList = GetParagraphList(question)
    question = question.replace('"', "'")
    current_dir = os.path.dirname(__file__)

    TFIDFDataPath = os.path.join(
        current_dir, '..', 'data', 'TFIDFDataPath.json')
    # TFIDFDataPath = "../data/TFIDFDataPath.json"
    TFIDFembeddingPath = os.path.join(
        current_dir, '..', 'data', 'TFIDFembeddingPath.json')
    # TFIDFembeddingPath = "../data/TFIDFembeddingPath.json"

    isFirst = True
    num = 0

    TFIDFDataFile = open(TFIDFDataPath, "a")
    TFIDFDataFile.truncate(0)
    TFIDFDataFile.write("{\n")
    for paragraph in paragraphList:
        if isFirst == False:
            TFIDFDataFile.write(",\n")
        isFirst = False
        TFIDFDataFile.write(
            '"' + str(num) + '": { "content": "' + paragraph + '"}')
        num += 1
    TFIDFDataFile.write("\n}")
    TFIDFDataFile.close()
    dealEnglishData(TFIDFDataPath, TFIDFembeddingPath)

    Tfidf = tfidf(TFIDFDataPath, TFIDFembeddingPath)
    return Tfidf.search(question, k)
