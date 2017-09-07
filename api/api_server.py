from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
import random

app = Flask(__name__)

es = Elasticsearch([{'host': '192.168.2.10', 'port': 9200}])


def detail_format(results):
    print("GET detail")
    question_aspect = '餐廳'
    
    res = results.get('hits').get('hits')[0].get('_source')

    result_mapping = {"title": str(res.get('name')),'buttons':[]}

    # text_content = str(res.get('name'))+"\n"
    subtitle = ""
    if res.get('categories')[0].get('name'):# category
        subtitle = subtitle + "這是一家" + str(res.get('categories')[0].get('name'))
        # text_content = text_content + str(res.get('categories')[0].get('name'))+"\n"

    if res.get('location').get('formattedAddress'):
        subtitle = subtitle + "位於" + "".join(reversed(res.get('location').get('formattedAddress')))
        # text_content = text_content + '地址：' + "".join(reversed(res.get('location').get('formattedAddress')))+"\n"
    else:
        subtitle = subtitle

    if res.get('stats').get('checkinsCount'):
        subtitle = subtitle + '總共有' + str(res.get('stats').get('checkinsCount'))+"人在這打過卡！"
        # text_content = text_content + '總共有' + str(res.get('stats').get('checkinsCount'))+"人在這打過卡！\n"

    if res.get('contact').get('formattedPhone'):# phone
        result_mapping['buttons'].append({"type":"phone_number","phone_number":str(res.get('contact').get('formattedPhone')),"title":"打電話"})
        # subtitle = subtitle + '電話：' + str(res.get('contact').get('formattedPhone'))

    result_mapping['subtitle'] = subtitle
    # if res.get('tips').get('count')>0:
    #     text_content = text_content + '有人評論說：' + str(res.get('tips').get('items')[random.choice(range(res.get('tips').get('count')))].get('text'))+"\n"

    emotion_list = [('love','😍'),('haha','😃'),('angry','😠'),('wow','😮'),('sad','😭')]


    for emotion, emoji in emotion_list:
        if res.get('emotion').get(emotion).get('count') > 0:
            comment = res.get('emotion').get(emotion).get('content')[random.choice(range(res.get('emotion').get(emotion).get('count')))]
            result_mapping['buttons'].append({"set_attributes": {"emotion": "haha","rh_id":res.get('id')},
                "block_names": ["emotion_comment"],"type": "show_block","title": "{}篇{}評論:{}".format(res.get('emotion').get(emotion).get('count'),emoji,comment)})
    # result_mapping['buttons'].append({"set_attributes": {"emotion": "haha","rh_id":res.get('id')},
    #             "block_names": ["emotion_comment"],"type": "show_block","title": "😃😭😍😮😠"})
    if len(result_mapping['buttons'])==0: result_mapping.pop("buttons", None)

    reply_dict = {"messages": [{"attachment": {"type": "template","payload": {"template_type": "generic","elements": []}}}]}
    # reply_dict['messages'].append({"text": text_content})
    reply_dict['messages'][0]['attachment']['payload']['elements'].append(result_mapping)

    print(reply_dict)
    return reply_dict


def gallery_format(results):
    print("Get Gallery")
    results = results.get('hits').get('hits')

    reply_dict = {"messages": [{"attachment": {"type": "template","payload": {"template_type": "generic","elements": []}}}]}

    for res in results[:3]:
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
        reply_dict['messages'][0]['attachment']['payload']['elements'].append(
            { "title": title,
              "image_url": img_url,
              "subtitle": subtitle,
              "buttons": [
                {
                  "type": "web_url",
                  "url": res.get('url'),
                  "title": "查看食記"
                },
                {
                  "set_attributes": {
                    "article_id": res.get('article_id')
                  },
                  "block_names": [
                    "object name and evaluation"
                  ],
                  "type": "show_block",
                  "title": "了解更多"
                }
              ]
            })
    return reply_dict

@app.route('/gallery/v1.0/random', methods=['GET'])
def get_gallery():
    question_aspect = request.args['question_aspect']
    print(question_aspect)
    res = es.search(index="pixnet", doc_type="food", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
    # if question_aspect =='餐廳':
        # res = es.search(index="pixnet", doc_type="food", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
    # elif question_aspect =='住宿':
        # res = es.search(index="pixnet", doc_type="hotel", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
    return jsonify(gallery_format(res))



@app.route('/test/detail/v1.0/random', methods=['GET'])
def get_tasks():
    res = es.search(index="pixnet", doc_type="foursquare", body={"size": 1,"query": {"function_score": {"random_score": {}}}})
    return jsonify(detail_format(res))

@app.route('/test/gallery/v1.0/random', methods=['GET'])
def get_tgallery():
    res = es.search(index="pixnet", doc_type="food", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
    # if question_aspect =='餐廳':
        # res = es.search(index="pixnet", doc_type="food", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
    # elif question_aspect =='住宿':
        # res = es.search(index="pixnet", doc_type="hotel", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
    return jsonify(gallery_format(res))

@app.route('/gallery/v1.0/keyword', methods=['GET'])
def get_gallery_by_keyword():
    query = {"query": {
        "bool": {
          "must": [
            {
              "match_phrase": {
                "tags": "大安區"
              }
            },
            {
              "match_phrase": {
                "content": "西班牙"
              }
            }
          ]
        }
    }}
    res = es.search(index="pixnet", doc_type="food", body=query)
    return jsonify(gallery_format(res))

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
