from html.parser import HTMLParser
import json
import os
import requests
from bs4 import BeautifulSoup
import math
from fake_useragent import UserAgent


class Data:
    def __init__(self, query="", paragraph=[]):
        self.queryStr = query
        self.paragraphList = paragraph

    def writeOneJson(self, filePath, mode):
        with open(filePath, mode) as f:
            f.write('{"query": "')
            f.write(self.queryStr)
            f.write('","paragraph": ')
            jsonStr = json.dumps(self.paragraphList)
            f.write(jsonStr)
            f.write("}\n")


class HTMLCleaner(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(HTMLCleaner, self).__init__(*args, **kwargs)
        self.data_list = []

    def handle_data(self, data):
        self.data_list.append(data)


def readMultiJson(filename):
    resultJsonList = []
    with open(filename, "r") as f:
        upToNowStr = ""
        nowStr = ""
        for line in f:
            nowStr = line
            upToNowStr += nowStr
            if nowStr == "}\n":
                resultJsonList.append(json.loads(upToNowStr))
                upToNowStr = ""
    return resultJsonList


def queryProcess(queryStr):
    return queryStr[23:].replace("\"", "'")


def contextProcess(contextStr):
    contextStr = contextStr.replace("\"", "'")
    contextStrList = contextStr.split("\n")
    contextRetList = []
    contextCount = 0
    contextUpToNow = ""
    MAXToken = 150
    for context in contextStrList:
        if len(context) == 0:
            continue
        if contextCount < 6:
            contextUpToNow = contextUpToNow + " " + context
        else:
            for i in range(math.floor(len(contextUpToNow) / MAXToken)):
                contextRetList.append(
                    contextUpToNow[i*MAXToken:((i+1)*MAXToken)])
            contextRetList.append(
                contextUpToNow[(math.floor(len(contextUpToNow) / MAXToken)) * MAXToken:])
            contextUpToNow = ""
            contextCount = 0
        contextCount += 1
    if len(contextUpToNow):
        for i in range(math.floor(len(contextUpToNow) / MAXToken)):
            contextRetList.append(
                contextUpToNow[i*MAXToken:((i+1)*MAXToken)])
        contextRetList.append(
            contextUpToNow[(math.floor(len(contextUpToNow) / MAXToken)) * MAXToken:])
    # theMaxNum = 0
    # for i in contextRetList:
    #     theMaxNum = max(theMaxNum, len(i))
    # print("max token number: ", theMaxNum)
    return contextRetList
# is 'best offer' a good moive?


def getContext(link):
    conn_timeout = 6
    read_timeout = 6
    timeouts = (conn_timeout, read_timeout)
    ua = UserAgent()
    try:
        r = requests.get(
            link, headers={"User-Agent": ua.random}, timeout=timeouts)
    except requests.exceptions.ConnectionError as e:
        print("run into ConnectionError when link is :", link,
              "\nerror ", e)
        return []
    except requests.exceptions.ReadTimeout as e:
        print("run into ReadTimeout when link is :", link,
              "\nerror ", e)
        return []
    except requests.exceptions.TooManyRedirects as e:
        print("run into TooManyRedirects when link is :", link,
              "\nerror ", e)
        return []

    r.encoding = 'UTF-8'
    if r.status_code == requests.codes.ok:
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
        except AssertionError as e:
            print("run into AssertionError when link is :", link,
                  "\nerror ", e)
            return []

        contextList = soup.find_all('p')
        cleaner = HTMLCleaner()
        for c in contextList:
            # print("c:", c.text)
            paragraphList = contextProcess(
                c.text.replace('\n', '').replace('\r', '').replace("\t", " "))
            for paragraph in paragraphList:
                # print("    paragraph:", paragraph)
                cleaner.feed(paragraph)
        return cleaner.data_list
    else:
        print("run into error when link is :", link,
              "\nerror code:", r.status_code)
        return []


def GetParagraphFromLinks(LinkList):
    retLink = []
    for link in LinkList:
        ContextList = getContext(link)
        for paragraph in ContextList:
            retLink.append(paragraph)
    return retLink
