from elasticsearch import Elasticsearch
import elasticsearch.helpers
from datetime import datetime
import urllib.request
import json
import time
import re

# Prepare query 
header={'Content-Type': 'application/json'}
req_ch = urllib.request.Request(url='http://192.168.2.100:5678/chuck/couple_all', headers=header, method='POST')
req_en = urllib.request.Request(url='http://192.168.2.30:8080/webresources/jammin/emotion', headers=header, method='POST')

def queryEmotion_ch(content_list):
    # Prepare query data
    query = {"data":[]}
    for text in content_list[:int(len(content_list)/1.5)]:
        query["data"].append({"message":text.strip()})

    header={'Content-Type': 'application/json'}
    
    query_str = json.dumps(query)
    # Query
    res = urllib.request.urlopen(req_ch, query_str.encode())
    res_json = json.loads(res.read().decode())

    return res_json

def queryEmotion_en(content_list):
    # Prepare query data
    res_json = []
    for text in content_list:
        query = {"text":text,"lang":"en"}
        query_str = json.dumps(query)
        # Query
        res = urllib.request.urlopen(req_en, query_str.encode())
        res_json.append(json.loads(res.read().decode()))
    
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

def organize_emotion_en(emotion_json):
    emotion_dict = {'wow':{'count':0, 'content':[]},
                'love':{'count':0, 'content':[]},
                'haha':{'count':0, 'content':[]},
                'sad':{'count':0, 'content':[]},
                'angry':{'count':0, 'content':[]}}
    emotion_eight2five = {
        "anger":"angry",
        "sadness":"sad",
        "joy":"haha",
        "fear":"sad",
        "disgust":"sad",
        "trust":"love",
        "anticipation":"love",
        "surprise":"wow"
    }
    for sentence_res in emotion_json:
        if sentence_res['ambiguous']!= 'yes':
            emo = emotion_eight2five[sentence_res['groups'][0]['name']]
            emotion_dict[emo]['count'] = emotion_dict[emo]['count'] +1
            emotion_dict[emo]['content'].append(sentence_res['text'])
    
    return emotion_dict

if __name__ == '__main__':
    

    es = Elasticsearch([{'host': '192.168.2.10', 'port': 9200}])
    doc_table = "foursquare"

    # Take all pixnet result
    # docs = list(elasticsearch.helpers.scan(es, index="pixnet", doc_type=doc_table)) #not doc['_source'].get('emotion') or 
    # total_content = [(doc['_id'],doc['_source'].get('content')) for doc in docs if not doc['_source'].get('emotion')] # if doc['_source'].get('emotion').get('love').get('count')+doc['_source'].get('emotion').get('haha').get('count')+doc['_source'].get('emotion').get('sad').get('count')+doc['_source'].get('emotion').get('angry').get('count')+doc['_source'].get('emotion').get('wow').get('count')==0
    # print('Total index: ', len(total_content))

    # print('Query Emotion for each sentence')

    # for pid, content in total_content:
        # print('Quering & Updating', pid)
        # emotion_dict = organize_emotion_ch(queryEmotion_ch(list(filter(lambda a: a.strip() != '', filter(None, re.split("[。\n]", content))))))
        # es.update(index='pixnet', doc_type=doc_table, id=pid, body={"doc": {"emotion": emotion_dict}})
        # time.sleep(0.5)

    # Take all hotel/restaurant result
    docs = list(elasticsearch.helpers.scan(es, index="pixnet", doc_type=doc_table)) #not doc['_source'].get('emotion') or 
    total_content = [(doc['_id'],[comment for comment in doc['_source'].get('tips').get('items')]) for doc in docs if doc['_source'].get('tips') if not doc['_source'].get('emotion')] # if doc['_source'].get('emotion').get('love').get('count')+doc['_source'].get('emotion').get('haha').get('count')+doc['_source'].get('emotion').get('sad').get('count')+doc['_source'].get('emotion').get('angry').get('count')+doc['_source'].get('emotion').get('wow').get('count')==0
    print('Total index: ', len(total_content))

    # print('Query Emotion for each sentence')
    for pid, contents in total_content:
        print('Quering & Updating', pid, len(contents))
        
        ch_query_contents = []
        en_query_contents = []
        for content in contents:
            if content.get("lang") =='en':
                for _ in range(content.get('agreeCount')+1):
                    en_query_contents.append(content.get('text'))
            if content.get("lang") == "zh":
                for _ in range(content.get('agreeCount')+1):
                    ch_query_contents.append(content.get('text'))

        ch_emotion_dict = {}
        en_emotion_dict = {
                'wow':{'count':0, 'content':[]},
                'love':{'count':0, 'content':[]},
                'haha':{'count':0, 'content':[]},
                'sad':{'count':0, 'content':[]},
                'angry':{'count':0, 'content':[]}
                }
        if len(ch_query_contents) >0:
            ch_emotion_dict = organize_emotion_ch(queryEmotion_ch(ch_query_contents))
        if len(en_query_contents) >0:
            en_emotion_dict = organize_emotion_en(queryEmotion_en(en_query_contents))
        
        # Union two dict
        for emo, val in ch_emotion_dict.items():
            en_emotion_dict[emo]['count'] = en_emotion_dict[emo]['count'] + val.get('count')
            en_emotion_dict[emo]['content'] = en_emotion_dict[emo]['content'] + [v for v in val.get('content')]
        
        es.update(index='pixnet', doc_type=doc_table, id=pid, body={"doc": {"emotion": en_emotion_dict}})



    
    
