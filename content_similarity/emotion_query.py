from elasticsearch import Elasticsearch
import elasticsearch.helpers
from datetime import datetime
import urllib.request
import json
import time
import re
def queryEmotion(content_list):
    # Prepare query data
    query = {"data":[]}
    for text in content_list:
        query["data"].append({"message":text})

    header={'Content-Type': 'application/json'}
    req = urllib.request.Request(url='http://192.168.2.100:5678/chuck/couple_all', headers=header, method='POST')
    query_str = json.dumps(query)
    # Query
    res = urllib.request.urlopen(req, query_str.encode())
    res_json = json.loads(res.read().decode())

    return res_json

def organize_emotion(emotion_json):
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

if __name__ == '__main__':
    

    es = Elasticsearch([{'host': '192.168.2.10', 'port': 9200}])
    doc_table = "food"

    # Take all result
    docs = list(elasticsearch.helpers.scan(es, index="pixnet", doc_type=doc_table)) #not doc['_source'].get('emotion') or 
    total_content = [(doc['_id'],doc['_source'].get('content')) for doc in docs if doc['_source'].get('emotion').get('love').get('count')+doc['_source'].get('emotion').get('haha').get('count')+doc['_source'].get('emotion').get('sad').get('count')+doc['_source'].get('emotion').get('angry').get('count')+doc['_source'].get('emotion').get('wow').get('count')==0]
    print('Total index: ', len(total_content))

    print('Query Emotion for each sentence')

    for pid, content in total_content:
        print('Quering & Updating', pid)
        emotion_dict = organize_emotion(queryEmotion(list(filter(None, re.split("[。\n]", content)))))
        es.update(index='pixnet', doc_type=doc_table, id=pid, body={"doc": {"emotion": emotion_dict}})
        time.sleep(0.5)

    
    
