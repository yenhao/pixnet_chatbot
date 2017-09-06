from elasticsearch import Elasticsearch
import elasticsearch.helpers
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

es = Elasticsearch()

es = Elasticsearch([{'host': '192.168.2.10', 'port': 9200}])

# food_shit = [39277209,387048788,104091918,372270479,337462112,370222286,31464855,23979807,32425198,43535738,61163026,61222765,42779873,27305159,30564884,30618482,8965237,362086491,106293227,105208937,50418224,103006564,101788465,103759531,102345676,43224901,43243567,43252288,43721611,43773316,45981428,2047159]
folder = "../data/article/"

# Retrieve data from file
for file_name in os.listdir(folder):
    print(file_name)
    with open(folder + file_name) as file:
        for i, line in enumerate(file.readlines()):
            try:
	            soup = BeautifulSoup(data['content'], "html.parser")
	            img_list = [img_tag.get('src') for img_tag in soup.find_all('img')]
	            print(data.get('article_id'))
	            print(img_list)
	            es.update(index='pixnet', doc_type=file_name.split('.')[0], id=data.get('article_id'), body={"doc": {"images": img_list}})
            except:
                print(line)
                continue
