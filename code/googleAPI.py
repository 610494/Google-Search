import requests
import time
import random
import json
from fake_useragent import UserAgent

ip_pool = [
    '119.98.44.192:8118',
    '111.198.219.151:8118',
    '101.86.86.101:8118',
]


def ip_proxy():
    ip = ip_pool[random.randrange(0, 3)]
    proxy_ip = 'http://'+ip
    proxies = {'http': proxy_ip}
    return proxies


def URLGenerator(base, key, ID, query):
    searchURL = base
    searchURL += "key=" + key
    searchURL += "&cx=" + ID
    searchURL += "&q=" + query
    return searchURL


def GetLink(googleResult):
    retList = []
    resultJson = json.loads(googleResult)
    if "items" in resultJson:
        items = resultJson["items"]
        for item in items:
            retList.append(item["link"])
    else:
        return []
    return retList


def Search(question):

    APIKeyList = []
    searchEngineID = " "
    googleAPISetting = "../data/googleAPI.json"
    with open(googleAPISetting, "r") as googleAPI:
        APISetting = json.load(googleAPI)
        APIKeyList = APISetting["APIKeyList"]
        searchEngineID = APISetting["searchEngineID"]

    linkList = []
    APIKey = 0
    waitingTime = 1
    BaseURL = "https://www.googleapis.com/customsearch/v1?"

    searchURL = URLGenerator(
        BaseURL, APIKeyList[APIKey], searchEngineID, question)

    ua = UserAgent()

    r = requests.get(searchURL,  headers={
        "User-Agent": ua.random}, proxies=ip_proxy())
    if r.status_code == requests.codes.ok:
        linkList = GetLink(r.text)
    # 402 mean over the budget
    elif r.status_code == 402:
        APIKey = (APIKey + 1) % len(APIKeyList)
        if APIKey == 0:
            print("budget is , please try tomorrow")
    elif r.status_code == 429:
        print("run into rateLimitExceeded, wait for ", waitingTime, "s")
        time.sleep(waitingTime)
        print("finish waiting")
        waitingTime *= 2
        if waitingTime > 3600:
            print("waiting to long, program force close")
            return []
        APIKey = (APIKey + 1) % len(APIKeyList)
        if APIKey == 0:
            print("budget is , please try tomorrow")
            return []
    else:
        print("run into error when q is :", question,
              "\nerror code:", r.status_code)
    return linkList
