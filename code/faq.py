import json
import os
from collections import OrderedDict


class tfidf:
    def __init__(self, datasetPath, embeddingPath):
        self.dataset = os.path.abspath(datasetPath)
        self.dataEmbedding = os.path.abspath(embeddingPath)
        self.questionsVec = []
        self.questionsList = []

        with open(self.dataset, 'r', encoding="utf-8") as data:
            jsonObj = data.read()
            parseJson = json.loads(jsonObj,  object_pairs_hook=OrderedDict)
            for paragraphID in parseJson:
                questionVec = {}
                self.questionsList.append(parseJson[paragraphID])

        with open(self.dataEmbedding, 'r', encoding="utf-8") as data:
            jsonObj = data.readline()
            while jsonObj:
                vec = json.loads(jsonObj,  object_pairs_hook=OrderedDict)
                self.questionsVec.append(vec)
                jsonObj = data.readline()

    def search(self, query, k):
        queryWordList = query.split(' ')
        queryVec = {}
        for word in queryWordList:
            queryVec[word] = queryVec.get(word, 0) + 1
        disQuery = 0
        for w in queryVec.values():
            disQuery += w**2
        disQuery = disQuery**(0.5)

        similarQuestionDict = {}

        for ids, question in enumerate(self.questionsVec):
            product = 0
            for word in queryVec:
                product += queryVec[word] * question.get(word, 0)

            disQuestion = 0
            for w in question.values():
                disQuestion += w**2
            disQuestion = disQuestion**(0.5)
            if disQuestion == 0:
                similarQuestionDict[ids] = 0
            else:
                similarQuestionDict[ids] = product / (disQuery * disQuestion)

        sortSimilarQuestionDict = sorted(
            similarQuestionDict.items(), key=lambda x: x[1], reverse=True)
        # print(sortSimilarQuestionDict)
        # print("sortSimilarQuestionDict type:", type(sortSimilarQuestionDict))

        sortSimilarQuestion = []
        for QuestionID in range(k):
            Question = sortSimilarQuestionDict[QuestionID]
            sortSimilarQuestion.append(
                self.questionsList[Question[0]]["content"])
        return sortSimilarQuestion
