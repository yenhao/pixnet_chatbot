import urllib.request
import json
import time
import string
import re
import sys
from elasticsearch import Elasticsearch
from get_contact_info import *

# Prepare query 
header={'Content-Type': 'application/json'}
req_ch = urllib.request.Request(url='http://140.114.77.23:5678/chuck/couple_all', headers=header, method='POST')


def readJSONFromFile(filename):
    with open(filename) as open_file:
        data = open_file.readline()
        data = json.loads(data)

    return data



def queryEmotion_ch(content_list):
    # Prepare query data
    query = {"data":[]}
    for text in content_list:
        query["data"].append({"message":text.strip()})
    
    query_str = json.dumps(query)
    # query
    res = urllib.request.urlopen(req_ch, query_str.encode())
    res_json = json.loads(res.read().decode())
    return res_json



def organize_emotion_ch(emotion_json):
    emotion_dict = {'wow':{'count':0, 'content':[]},
                'love':{'count':0, 'content':[]},
                'haha':{'count':0, 'content':[]},
                'sad':{'count':0, 'content':[]},
                'angry':{'count':0, 'content':[]}}

    for sentence_res in emotion_json['data']:
        if sentence_res['ambiguous']!= True:
            if sentence_res['emotion1'] == 'angry':
                if sentence_res['emotion2'] == 'haha' or sentence_res['emotion2'] == 'love': continue            
            emotion_dict[sentence_res['emotion1']]['count'] = emotion_dict[sentence_res['emotion1']]['count'] +1
            emotion_dict[sentence_res['emotion1']]['content'].append(sentence_res['message'])
    
    return emotion_dict



def convertToCorrespondJSON(data):
    print("{0}\t{1}".format(data["Article_id"], data["Title"]))
    new_json = {"emotion":{},"fb":{"restaurant_specialties":None,"talking_about_count":None,"rating_count":None,"website":None,"overall_start_rating":None,"restaurant_services":None,"checkings":None,"phone":None,"category":None},"contact":{"phone":None,"formattedPhone":None},"referralId":None,"categories":[{"name":None,"shortName":None,"pluralName":None,"id":None,"primary":True,"icon":{"suffix":None,"prefix":None}}],"hasPerk":False,"stats":{"tipCount":0,"checkinsCount":0,"usersCount":0},"verified":False,"location":{"lat":None,"lng":None,"postalCode":None,"formattedAddress":[]},"id":None,"specials":{"count":0,"items":[]},"venueChains":[],"name":None,"tips":{"count":0,"id":None,"items":[{"createdAt":None,"agreeCount":0,"count":None,"text":[]}]}}
    res_json = queryEmotion_ch(list(filter(lambda a: a.strip() != '', filter(None, re.split("[。\n]", data["Content"])))))
    emotion_dict = organize_emotion_ch(res_json)
    address, phone = getContactInfo(data["Content"])
    print("Contact:{0}\t{1}".format(address, phone))
    
    name = data["Title"]
    name = re.sub("食記", "", name)
    name = re.sub("\[", "", name)
    name = re.sub("\]", "", name)
    pattern = r"[{}]".format(string.punctuation)
    name = re.sub(pattern, "", name)
    name = re.sub(" ", "", name)

    new_json["name"] = name
    new_json["id"] = data["Article_id"]
    new_json["emotion"] = emotion_dict
    new_json["location"]["formattedAddress"] = address
    new_json["contact"]["phone"] = phone
    return new_json


def insertIntoElasticsearch(doc):
    # ElasticSearch settings
    ES_HOST = {"host": "140.114.77.24", "port": 9200}
    ES_INDEX = 'pixnet'
    ES_TYPE = 'foursquare'
    es = Elasticsearch([ES_HOST])
    es.index(index=ES_INDEX, doc_type=ES_TYPE, id=doc['id'], body=doc)



if __name__ == '__main__':
    filename = sys.argv[1]
    data = readJSONFromFile(filename)
    length = len(data)
    for i, article in enumerate(data):
        if (i+1) % 100 == 0:
            print("=== {0} articles inserted... ===".format(i+1))
        new_json = convertToCorrespondJSON(article)
        # print(new_json["location"])
        # break
        insertIntoElasticsearch(new_json)
