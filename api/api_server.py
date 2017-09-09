from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from pixnet_search_es import *
import random
import requests
import json
import re
import urllib.request

app = Flask(__name__)

es = Elasticsearch([{'host': '192.168.2.10', 'port': 9200}])
header={'Content-Type': 'application/json'}
req_ch = urllib.request.Request(url='http://140.114.77.23:5678/chuck/couple_all', headers=header, method='POST')

cate_list = []

x = requests.get("http://140.114.77.24:9200/_mapping?pretty").text
x = json_acceptable_string = x.replace("'", "\"")
d = json.loads(x)
for cate in d["pixnet"]["mappings"]:
    cate_list += [cate]

print(cate_list)
def queryEmotion_ch(content_list):
    # Prepare query data
    query = {"data":[]}
    for text in content_list:
        query["data"].append({"message":text.strip()})

    header={'Content-Type': 'application/json'}
    
    query_str = json.dumps(query)
    # Query
    res = urllib.request.urlopen(req_ch, query_str.encode())
    res_json = json.loads(res.read().decode())

    return res_json

def organize_emotion_ch(emotion_json):
    
    emotion_list = []
    for sentence_res in emotion_json['data']:
        # if sentence_res['ambiguous']!= True:
        if sentence_res['emotion1'] == 'angry':
            if sentence_res['emotion2'] == 'haha' or sentence_res['emotion2'] == 'love': continue  
        emotion_list.append((sentence_res['emotion1'], sentence_res['message']))
    
    return emotion_list

API_Keys = [
    "AIzaSyCs1FDXEQhfcIvQSE_5oc064meaMjuEyt4"
]

def nearby_search(lat, lng, r):
    r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?'+
                    'location='+str(lat)+','+str(lng)+'&'+
                    'radius='+str(r)+'&'+
                    'type=restaurant&'+
                    'key='+API_Keys[random.randint(0, len(API_Keys)-1)])
    res = json.loads(r.text)
    
    item_list = []
    
    for item in res['results']:
        item_list.append({
            "name":item['name'],
            "place ID":item['place_id'],
            "rating":item['rating']
        })
        
    return item_list

def get_place_details(placeid, lang):
    key = API_Keys[random.randint(0, len(API_Keys)-1)]
    #key = 'AIzaSyAI63lmhEzMusGQXS_c43KK10ylY-q73NY'
    url = 'https://maps.googleapis.com/maps/api/place/details/json?'+ \
                    'placeid='+placeid+'&'+ \
                    'language='+lang+'&'+ \
                    'key='+ key
    r = requests.get(url)
    res = json.loads(r.text)
    
    try:
        if 'reviews' in res['result']:
            rev = res['result']['reviews']
        else:
            rev = []
        if "formatted_address" in res['result']:
            addr = res['result']["formatted_address"]
        else:
            addr = ""
        if "formatted_phone_number" in res['result']:
            tel = res['result']["formatted_phone_number"]
        else:
            tel = ""
        return {"formatted_address":addr, \
                "formatted_phone_number":tel, \
                "reviews":rev}
    except Exception as e:
        print(key)
        print(res)
        raise KeyError("Error")

# show comment
def comment_format(results,emotion):
    print("GET comment")
    
    emotion_list = {'love':'😍','haha':'😃','angry':'😠','wow':'😮','sad':'😭'}
    
    print(results)

    emotion_comment_list = results.get('hits').get('hits')[0].get('_source').get('emotion').get(emotion).get("content")

    text_content = "關於{}的評論有:".format(emotion_list[emotion])
    
    for emotion_comment in random.sample(emotion_comment_list, len(emotion_comment_list))[:3]:
        text_content = text_content + " \n\n『" +  emotion_comment + "』"

    reply_dict = {'messages':[]}
    reply_dict['messages'].append({"text": text_content})
    print(reply_dict)
    return reply_dict

def nearby_comment_format(results):
    print("GET Nearby Comment")
    
    emotion_dict = {'love':'😍','haha':'😃','angry':'😠','wow':'😮','sad':'😭'}
    
    reviews = results.get('reviews')

    print("Query Emotion")
    review_contents = [review_content.get('text') for review_content in reviews]
    emotion_list = organize_emotion_ch(queryEmotion_ch(review_contents))
    # result_mapping = {}
    # result_mapping = {"title": "評論與他們的情緒們",'buttons':[]}

    # if res.get('contact').get('formattedPhone'):# phone
        # result_mapping['buttons'].append({"type":"phone_number","phone_number":str(res.get('contact').get('formattedPhone')),"title":"打電話"})
    

    # emotion_comment_list = results.get('hits').get('hits')[0].get('_source').get('emotion').get(emotion).get("content")

    # text_content = "關於{}的評論有:".format(emotion_list[emotion])
    
    # for emotion_comment in random.sample(emotion_comment_list, len(emotion_comment_list))[:3]:
    #     text_content = text_content + " \n\n『" +  emotion_comment + "』"

    # reply_dict = {"messages": [{"attachment": {"type": "template","payload": {"template_type": "generic","elements": []}}}]}
    
    # reply_dict['messages'][0]['attachment']['payload']['elements'].append(result_mapping)

    text = "評論與他們的情緒們\n"

    for emotion, content in emotion_list:
        text += '『' + emotion_dict[emotion] + " - " + content + '』\n\n'

    reply_dict = {'messages':[]}

    reply_dict['messages'].append({"text": text})
    print(reply_dict)
    return reply_dict

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
        subtitle = subtitle + "，位於" + "".join(reversed(res.get('location').get('formattedAddress')))
        # text_content = text_content + '地址：' + "".join(reversed(res.get('location').get('formattedAddress')))+"\n"
    else:
        subtitle = subtitle

    if res.get('stats').get('checkinsCount'):
        subtitle = subtitle + '。總共有' + str(res.get('stats').get('checkinsCount'))+"人在這打過卡！"
        # text_content = text_content + '總共有' + str(res.get('stats').get('checkinsCount'))+"人在這打過卡！\n"

    if res.get('contact').get('formattedPhone'):# phone
        result_mapping['buttons'].append({"type":"phone_number","phone_number":str(res.get('contact').get('formattedPhone')),"title":"打電話"})
        # subtitle = subtitle + '電話：' + str(res.get('contact').get('formattedPhone'))

    if subtitle == '': subtitle = '看看評論吧！'
    result_mapping['subtitle'] = subtitle
 
    emotion_list = [('love','😍'),('haha','😃'),('angry','😠'),('wow','😮'),('sad','😭')]

    emo_count = 0
    for emotion, emoji in emotion_list[:3]:
        # result_mapping['buttons'].append({"set_attributes": {"emotion": "haha","rh_id":res.get('id')},
                # "block_names": ["emotion_comment"],"type": "show_block","title": "有{}篇{}的評論".format(3,emoji)})
        if res.get('emotion').get(emotion).get('count') > 0:
            comment = res.get('emotion').get(emotion).get('content')[random.choice(range(res.get('emotion').get(emotion).get('count')))]
            result_mapping['buttons'].append({"set_attributes": {"emotion": emoji,"rh_id":res.get('id')},
                "block_names": ["emotion_comment"],"type": "show_block","title": "查看{}篇{}的評論".format(res.get('emotion').get(emotion).get('count'),emoji)})
            emo_count = emo_count + 1
            print(emo_count)
            if emo_count >3:break
    # result_mapping['buttons'].append({"set_attributes": {"emotion": "haha","rh_id":res.get('id')},
    #             "block_names": ["emotion_comment"],"type": "show_block","title": "😃😭😍😮😠"})
    if len(result_mapping['buttons'])==0: result_mapping.pop("buttons", None)

    reply_dict = {"messages": [{"attachment": {"type": "template","payload": {"template_type": "generic","elements": []}}}]}
    # reply_dict['messages'].append({"text": text_content})
    reply_dict['messages'][0]['attachment']['payload']['elements'].append(result_mapping)

    print(reply_dict)
    return reply_dict


def nearby_gallery_format(results):
    print("Get Gallery")
    results = results.get('places')
    print(results)
    print(results[0])
    print(type(results))
    # check_blog = '查看食記'

    reply_dict = {"messages": [{"attachment": {"type": "template","payload": {"template_type": "generic","elements": []}}}]}
    print("Get Result Count: ", len(results))
    for res in results[:3]:
        title = res.get('name')
        place_id = res.get('place ID')
        details_zh = get_place_details(place_id, 'zh-TW')
        phone = details_zh.get('formatted_phone_number')
        address = details_zh.get("formatted_address") 
        subtitle = ""
        if address:
            subtitle += "位於：" + address + "，"

        btn = [
                {"set_attributes": {
                        "place_id": res.get('place ID')
                    },
                    "block_names": ["nearby_comment"],
                    "type": "show_block",
                    "title": "查看評論跟他們的情緒們～"
                }
              ]
        if phone :
            btn.append({"type":"phone_number","phone_number":str(phone).replace(" ",""),"title":"打電話"})
        # if res.get('images'):
        #   img_url = res.get('images')[random.choice(range(len(res.get('images'))))]
        # else:
        #   img_url = 'http://weclipart.com/gimg/87B5BD1C1C5CF590/no-camera-allowed-md.png'
        # if res.get('emotion'):
        #     sentences = [sentence.strip()for key, val in res.get('emotion').items() for sentence in val['content']]
        # else:
        #     sentences = []
        if res.get('rating'):
          subtitle += "這家餐廳的平均評分有" + str(res.get('rating')) + "分"
        else:
          subtitle += "看看評論吧！"

        reply_dict['messages'][0]['attachment']['payload']['elements'].append(
            { "title": title,
              # "image_url": img_url,
              "subtitle": subtitle,
              "buttons" : btn
            })
    return reply_dict

def gallery_format(results,question_aspect):
    print("Get Gallery")
    results = results.get('hits').get('hits')

    if question_aspect == '餐廳':
        check_blog = '查看食記'
    elif question_aspect == '住宿':
        check_blog = '查看遊記'

    reply_dict = {"messages": [{"attachment": {"type": "template","payload": {"template_type": "generic","elements": []}}}]}
    print("Get Result Count: ", len(results))
    for res in results[:5]:
        res = res.get('_source')
        if len(res.get('tags')) > 0:
          title = res.get('tags')[random.choice(range(len(res.get('tags'))))]
        else:
          title = res.get('title')
        if res.get('images'):
          img_url = res.get('images')[random.choice(range(len(res.get('images'))))]
        else:
          img_url = 'http://weclipart.com/gimg/87B5BD1C1C5CF590/no-camera-allowed-md.png'
        if res.get('emotion'):
            sentences = [sentence.strip()for key, val in res.get('emotion').items() for sentence in val['content']]
        else:
            sentences = []
        if len(sentences) == 0:
          subtitle = res.get('category')
        else:
          subtitle = sentences[random.choice(range(len(sentences)))].replace("\n","") 

        title = res.get('title')
        title = re.sub('[!@#$】►☆✰♥┃【]', '', title)
        title_tag = title_keyword(title)
        print("title tag : " , title_tag)
        # print("blog tag : ",hit['_source']['tags'])
        ## search more detail
        
        hits = question_match_query(title_tag)
        print(hits)
        btn2 = {}
        # title not found
        if hits == []:
            try:
                hits = question_match_query(res.get('tags'))
                # still not found
                if len(hits) == 0:
                    print("foursquare not found")
                    btn2 = {
                      "set_attributes": {
                        "article_id": 'qq_no_found',
                        "origin_id" : res.get('article_id')
                      },
                      "block_names": [
                        "object name and evaluation"
                      ],
                      "type": "show_block",
                      "title": "了解更多"
                }
                #found
                else:
                    hit = hits[0]
                    print("\tmatch_Title : ",hit['_source']['name'])
                    btn2 = {
                      "set_attributes": {
                        "article_id": hit['_source']['id'],
                        "origin_id" : res.get('article_id')
                      },
                      "block_names": [
                        "object name and evaluation"
                      ],
                      "type": "show_block",
                      "title": "了解更多"
                    }
            # error
            except:
                print("No Tag to search")
                btn2 = {
                  "set_attributes": {
                    "article_id": 'qq_no_found',
                    "origin_id" : res.get('article_id')
                  },
                  "block_names": [
                    "object name and evaluation"
                  ],
                  "type": "show_block",
                  "title": "了解更多"
                }
        # title found
        else:
            print("title match!")
            hit = hits[0]
            btn2 = {
                  "set_attributes": {
                    "article_id": hit['_source']['id'],
                    "origin_id" : res.get('article_id')
                  },
                  "block_names": [
                    "object name and evaluation"
                  ],
                  "type": "show_block",
                  "title": "了解更多"
                }


        reply_dict['messages'][0]['attachment']['payload']['elements'].append(
            { "title": title,
              "image_url": img_url,
              "subtitle": subtitle,
              "buttons": [
                {
                  "type": "web_url",
                  "url": res.get('url'),
                  "title": check_blog
                },btn2
                
              ]
            })
    return reply_dict

def match_query(title_tag , doctype , field_list):
    ## match search
    match_search = bulid_match_request( title_tag , field_list)
    res = es.search(index="pixnet", doc_type= doctype, body= match_search)

    hits = res['hits']['hits']

    return hits
def bulid_match_request( title_tag , field_list ):
    search_query = {
            "from" : 0, 
            "size" : 10,
            "query":{
                "bool": {
                              "should": []
                        }
                    }
    } 

    command = "match"
    q = search_query["query"]["bool"]
    for tag in title_tag:
        for f in field_list:
            q["should"] += [{command : {f : tag}}]  

    return search_query



def recommand_format(question_aspect, origin_id):
    print("GET recommend")
    if question_aspect == '餐廳':
        doc_type = 'food'
    else:
        doc_type ='travel_taiwan'

    query = {"size": 1,"query": {"match_phrase": {"article_id": origin_id}}}
    print(query)
    res = es.search(index="pixnet", doc_type=doc_type, body=query)
  
    hit = res.get('hits').get('hits')[0]


    title = hit['_source']['title']
    title = re.sub('[!@#$】►☆✰♥┃【]', '', title)
    title_tag = title_keyword(title)
    print()
    print("Title : ",hit['_source']['title'])
    print("title tag : " , title_tag)
    print("blog tag : ",hit['_source']['tags'])


    result_mapping = {"title": "您可能會對這個有興趣",'buttons':[]}

    # text_content = str(res.get('name'))+"\n"
    subtitle = "根據您的選擇，我們認為您可能會對這個有興趣～"
    
    count = 0
    # search more article from different category
    for cate in cate_list:
        if cate != doc_type:
            print(doc_type,"--->",cate)
            matches = match_query(title_tag , cate , ['title','tags'])
            if matches == []:
                matches = match_query(hit['_source']['tags'] , cate , ['title','tags'])
            for match in matches:    
                print("\tmatch_Title : ",match['_source']['title'])
                print("\tmatch_tags : ",match['_source']['tags'])

                result_mapping['buttons'].append({
                                  "type": "web_url",
                                  "url": match['_source']['url'],
                                  "title": match['_source']['title']
                                })
                count = count + 1
                print(count)
                break
        if count == 3: break
    
    if len(result_mapping['buttons'])==0: result_mapping.pop("buttons", None)

    reply_dict = {"messages": [{"attachment": {"type": "template","payload": {"template_type": "generic","elements": []}}}]}
    # reply_dict['messages'].append({"text": text_content})
    reply_dict['messages'][0]['attachment']['payload']['elements'].append(result_mapping)

    print(reply_dict)
    return reply_dict

@app.route('/comment/v1.0/show', methods=['GET'])
def get_emotion_comment():
    emotion_list_rev = {'😍':'love','😃':'haha','😠':'angry','😮':'wow','😭':'sad'}
    question_aspect = request.args['question_aspect']
    emotion = emotion_list_rev[request.args['emotion']]
    rh_id = request.args['rh_id']
    query = {"_source":["emotion.{}.content".format(emotion)],"size":1,"query":{"match":{"id.keyword":rh_id}}}
    
    if question_aspect == '餐廳':
        doc_type = 'foursquare'
    elif question_aspect == '住宿':
        doc_type = 'hotel'
    print(doc_type)
    print(query)
    res = es.search(index="pixnet", doc_type=doc_type, body=query)
    return jsonify(comment_format(res,emotion))

@app.route('/gallery/v1.0/question', methods=['GET'])
def ask_question():
    question_aspect = request.args['question_aspect']
    question = request.args['user_question']
    print("Aspect - {}, Question - {}, Keywords - {}".format(question_aspect,question,question_keyword(question)))
    if question_aspect == '餐廳':
        res = {"hits":{"hits":question_query(question)}}
        # res = es.search(index="pixnet", doc_type="food", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
        return jsonify(gallery_format(res,question_aspect))
    elif question_aspect == '住宿':
        res = {"hits":{"hits":question_query(question, 'taiwan_travel')}}
        # res = es.search(index="pixnet", doc_type="travel_taiwan", body={"size": 5,"query": {"function_score": {"random_score": {}}}})
        return jsonify(gallery_format(res,question_aspect))


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

@app.route('/detail/v1.0/id', methods=['GET'])
def get_detail_by_id():
    print("GET ID DETAIL")
    article_id = request.args['article_id']
    # origin_id = request.args['origin_id']
    if article_id == 'qq_no_found' :
        res = es.search(index="pixnet", doc_type="foursquare", body={"size": 1,"query": {"function_score": {"random_score": {}}}})
        return jsonify(detail_format(res))
    else :
        query = {"size": 1,"query": {"match_phrase": {"id": article_id}}}
        print(query)
        res = es.search(index="pixnet", doc_type="foursquare", body=query)
        return jsonify(detail_format(res))

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

@app.route('/detail/v1.0/nearby', methods=['GET'])
def get_near_by_gallery():
    print("GET LOCATION")
    longitude = request.args['longitude']
    latitude = request.args['latitude']
    places = nearby_search(latitude, longitude, "500")

    res = {"places" : []}
    for place in places[:3]:
        place_detail = {}
        # details_en = get_place_details(place['place ID'], 'en')
        # details_zh = get_place_details(place['place ID'], 'zh-TW')
        # place_detail['name'] = place
        # place_detail['detail'] = details_zh
        # print(place)
        # print(details_zh)
        res['places'].append(place)
   
    # res = es.search(index="pixnet", doc_type="food", body=query)
    return jsonify(nearby_gallery_format(res))

@app.route('/comment/v1.0/nearby', methods=['GET'])
def get_near_by_comment():
    print("GET Nearby Comment")
    place_id = request.args['place_id']
    details_zh = get_place_details(place_id, 'zh-TW')

    return jsonify(nearby_comment_format(details_zh))


@app.route('/recommand/v1.0/es', methods=['GET'])
def get_recommend():
    print("Get recommend!")
    question_aspect = request.args['question_aspect']
    origin_id = request.args['origin_id']

    return jsonify(recommand_format(question_aspect, origin_id))




if __name__ == '__main__':
    question = '今天晚餐要吃麥當勞'
    print(question_keyword(question))
    
    ## find lots of pixnet article
    # hits = question_query(question)

    ## print content
    # for hit in hits:
    #     print()
    #     print("Title : ",hit['_source']['title'])
    #     print("Tag : ",hit['_source']['tags'])
    #     print("img : ",imageurl_select(hit['_source']['images']))
    #     print("url : ",hit['_source']['url'])
    #     print("title tag : " ,title_keyword(hit['_source']['title']) )
    #     break

    app.run(host='0.0.0.0',debug=True)