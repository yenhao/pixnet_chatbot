from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

es = Elasticsearch()


# ignore 400 cause by IndexAlreadyExistsException when creating an index
# es.indices.create(index='test-index', ignore=400)

# ignore 404 and 400
# es.indices.delete(index='test-index', ignore=[400, 404])


# only wait for 1 second, regardless of the client's default
# es.cluster.health(wait_for_status='yellow', request_timeout=1)


folder = "../data/article/"

# Retrieve data from file
for file_name in os.listdir(folder):
    print(file_name)
    with open(os.listdir(folder) + file_name) as file:
        for i, line in enumerate(file.readlines()):
            try:
                data = json.loads(line)
                # To remove the html tags
                data['content'] = ''.join(BeautifulSoup(data['content']).findAll(text=True))
            except:
                print(line)
                continue
            es.index(index="pixnet", doc_type=file_name.split('.')[0], id=i+1, body=data)
