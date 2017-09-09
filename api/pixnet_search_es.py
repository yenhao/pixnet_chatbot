from __future__ import print_function
from bs4 import BeautifulSoup
from gensim.summarization import keywords
from time import time
import datetime
import json
import pprint
import copy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import random
import gensim
import jieba
import jieba.posseg as pseg
from re import compile as _Re
from gensim.models.word2vec import Word2Vec
from gensim.summarization import keywords

from Segmentor import *
segmenter= Segmentor()
tagger   = POSTagger()
import re

from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': '192.168.2.10', 'port': 9200}])


def content_segmentor(article):
    article = ""
    sentences = Tokenizer.ToSents(article)
    for sent in sentences :
        # 在斷詞
        words=segmenter.segment(sent)   
        if words != []:
            article += ' '.join(words)
    return article
def print_top_words(model, feature_names, n_top_words):
    
    topic_word = []
    for topic_idx, topic in enumerate(model.components_):        
#         print("Topic #%d:" % topic_idx)
#         print(" ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))        
        topic_word +=  [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        
    return list(set(topic_word))
def topic_modeling(content_data):
    n_features = 100
    n_topics   = 5
    n_top_words = 5
    
    stopwords = ['.','','?','!']
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=1,
                                       max_features=n_features,
                                       stop_words=stopwords)
    
    tfidf = tfidf_vectorizer.fit_transform(content_data)

    nmf   = NMF(n_components=n_topics , random_state=1 , alpha=.1 , l1_ratio=.5).fit(tfidf)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    topic_word          = print_top_words(nmf, tfidf_feature_names, n_top_words)
    
    return topic_word 

def title_extract(title_pair):
    good_phr = []
    bad_phr = []
    x = []
    i = 1
    ## 串起相同詞性的
    while i < len(title_pair):
        if title_pair[i-1][1][0] == title_pair[i][1][0] :
            if  title_pair[i-1] not in x :
                x.append(title_pair[i-1])
                x.append(title_pair[i])
            else :
                x.append(title_pair[i])
        else:
            if x != [] :
                x = "".join([a for a,b in x if b!='Nb'])
                if len(x) > 3:good_phr += [x]
                else : bad_phr += [x]
            x = []

        i = i + 1
    if good_phr == []:
        good_phr = ["".join(a for a,b in title_pair)]
    return good_phr , bad_phr

def title_keyword(title):
    ## Segmentor
    title_seg = segmenter.segment(title)
    title_tag = tagger.procSentStr(" ".join(title_seg))
    good_phr , bad_phr = title_extract(title_tag)
    
    ## Jieba
    

    return good_phr

def imgurl_random(soup):
    ## Random select img url
    imgs = soup.find_all('img')
    return imgs[ random.randint(0,int(len(imgs)/2))]['src']

# def cate_recognition(verb):
#     model = Word2Vec.load('./zh/zh.bin')
#     category_list = [('食','food'),('旅行','travel_taiwan')]
#     model.wv.similarity('吃', '吃')



def question_keyword(question):
    ## Segmentor
    question_seg = segmenter.segment(question)
    question_tag = tagger.procSentStr(" ".join(question_seg))
    
    N_index = []
    V_index = []
    
    ## Get N index
    for x,y in question_tag:
        if y == 'Nc' or y =='Nb' or y=="Na":
            N_index += [question_tag.index((x,y))]
        if y =='VE' or y=="VC":
            V_index += [question_tag.index((x,y))]
            
    ## bulid query attribute
    question_mean = []
    question_cate = []
    ## N
    for index in N_index:
        flag = 1
        for x,y in question_tag[:index]:    
            if x =='不要' or x =='不想' or x =='不':flag*=-1
        question_mean +=[(flag,question_tag[index][0])] 
#     ## Verb
#     for index in V_index:
#         cate = cate_recognition(question_tag[index])
#         question_cate +=[cate] 
    return question_mean 


def imageurl_select(url_list):
    for i in url_list:
        if not ( i.startswith('http://') or i.startswith('https://') ):
            url_list.remove(i)    
    return url_list[ random.randint(0,int(len(url_list)/2))]

def bulid_question_request(original_query , question, request_type):
    search_query = copy.deepcopy(original_query)
    if request_type == 'abs':
        field = 'tags'
        command = "match_phrase"
    if request_type == 'related':
        field = 'tags'
        command = "match"
    if request_type == 'content':
        field = 'content'
        command = "match"

    q = search_query["query"]["bool"]
    
    for i,j in question_keyword(question):
        if i == 1:
            q["must"] += [{command : {field : j}}]
        if i == -1:
            q["must_not"] += [{command : {field : j}}]    
    print(search_query)
    return search_query

def question_query(question, question_aspect = "food"):
    original_body = {
        "_source":["title","images","tags","url","emotion","article_id"],
        "from" : 0, 
        "size" : 20,
        "query":{
            "bool": {
                          "must": [],
                          "must_not": [],

                    }
                }
    } 
    ## abs
    search_body = bulid_question_request(original_body , question, 'abs')
    res = es.search(index="pixnet", doc_type=question_aspect, body= search_body)
    hits = res['hits']['hits']
    
    ## related
    if hits == []:
        search_body = bulid_question_request(original_body , question, 'related')
        res = es.search(index="pixnet", doc_type=question_aspect, body= search_body)
        hits = res['hits']['hits']
        
    ## content search
    if hits == []:
        print("content_search")
        search_body = bulid_question_request(original_body , question, 'content')
        res = es.search(index="pixnet", doc_type=question_aspect, body= search_body)
        hits = res['hits']['hits']
        
    return hits

def bulid_question_request_match(original_query , title_tag,):
    search_query = copy.deepcopy(original_query)

    field = ["name"]
    command = "match_phrase"
    q = search_query["query"]["bool"]
    for tag in title_tag:
        for f in field:
            q["should"] += [{command : {f : tag}}]  

    return search_query

def question_match_query(title_tag):
    original_body = {
#         "_source":["title","images","tags","url","content"],
        "from" : 0, 
        "size" : 10,
        "query":{
            "bool": {
                          "should": []
                    }
                }
    } 
    ## match search
    match_search = bulid_question_request_match(original_body , title_tag)
    res = es.search(index="pixnet", doc_type="foursquare", body= match_search)

    hits = res['hits']['hits']

    return hits
