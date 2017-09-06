from flask import Flask, jsonify
from elasticsearch import Elasticsearch
import random

app = Flask(__name__)

es = Elasticsearch([{'host': '192.168.2.10', 'port': 9200}])


def detail_format(results):
    print("GET detail")
    
    res = results.get('hits').get('hits')[0].get('_source')
    text_content = str(res.get('name'))+"\n"

    if res.get('categories')[0].get('name'):# category
        text_content = text_content + str(res.get('categories')[0].get('name'))+"\n"
    if res.get('contact').get('formattedPhone'):# phone
        text_content = text_content + '電話：' + str(res.get('contact').get('formattedPhone'))+"\n"

    if res.get('location').get('formattedAddress'):
        text_content = text_content + '地址：' + "".join(reversed(res.get('location').get('formattedAddress')))+"\n"

    # # if res.get('categories').get('name'):
    # #     text_content = text_content + '地址：' + str(res.get('categories').get('name'))+"\n"
    if res.get('stats').get('checkinsCount'):
        text_content = text_content + '總共有' + str(res.get('stats').get('checkinsCount'))+"人在這打過卡！\n"
    if res.get('tips').get('count')>0:
        text_content = text_content + '有人評論說：' + str(res.get('tips').get('items')[random.choice(range(res.get('tips').get('count')))].get('text'))+"\n"

    reply_dict = {"messages": []}
    reply_dict['messages'].append({"text": text_content})
    print(text_content)
    return reply_dict

def gallery_format(results):
    print("Get Gallery")
    results = results.get('hits').get('hits')

    reply_dict = {"messages": []}

    for res in results[:5]:
        res = res.get('_source')
        # print(res)
        if len(res.get('tags')) > 0:
          title = res.get('tags')[random.choice(range(len(res.get('tags'))))]
        else:
          title = res.get('title')
        if len(res.get('images')) > 0:
          img_url = res.get('images')[random.choice(range(len(res.get('images'))))]
        else:
          img_url = 'http://weclipart.com/gimg/87B5BD1C1C5CF590/no-camera-allowed-md.png'
        
        sentences = [sentence.strip()for key, val in res.get('emotion').items() for sentence in val['content']]
        if len(sentences) == 0:
          subtitle = res.get('category')
        else:
          subtitle = sentences[random.choice(range(len(sentences)))].replace("\n","") 
        reply_dict['messages'].append(
            {
              "attachment": {
                "type": "template",
                "payload": {
                  "template_type": "generic",
                  "elements": [
                    {
                      "title": title,
                      "image_url": img_url,
                      "subtitle": subtitle,
                      "buttons": [
                        {
                          "type": "web_url",
                          "url": res.get('url'),
                          "title": "Go to Article"
                        },
                        {
                          "set_attributes": {
                            "article_id": res.get('article_id')
                          },
                          "block_names": [
                            "object name and evaluation"
                          ],
                          "type": "show_block",
                          "title": "Show Details"
                        }
                      ]
                    }
                  ]
                }
              }
            })
    return reply_dict
    
 
def a():
    print('test')
    return {'qq':'ccc'}

@app.route('/test/detail/v1.0/random', methods=['GET'])
def get_tasks():
    res = es.search(index="pixnet", doc_type="foursquare", body={"size": 1,"query": {"function_score": {"random_score": {}}}})
    return jsonify(detail_format(res))

@app.route('/test/gallery/v1.0/random', methods=['GET'])
def get_tgallery():
    res = es.search(index="pixnet", doc_type="food", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
    return jsonify(gallery_format(res))

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
