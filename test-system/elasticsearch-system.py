# import Python's JSON library for its loads() method
import json

# import time for its sleep method
from time import sleep

# import the datetime libraries datetime.now() method
from datetime import datetime

# use the elasticsearch client's helpers class for _bulk API
from elasticsearch import Elasticsearch, helpers

# open elasticsearch client
client = Elasticsearch("localhost:9200")

"""
# load json as python dict
json_file = open('../output.json')

data = json.load(json_file)

# set scoring function s bm25
elasticsearch_response = helpers.bulk(client, data, index="covid_doc_bm25")

# print response
print ("helpers.bulk() RESPONSE:", json.dumps(elasticsearch_response, indent=4))
"""


with open('collection.json', "r", encoding="utf8") as f:
    data = json.load(f)

elasticsearch_response = helpers.bulk(client, data, index="latest_bm25")



q = "Covid-19 belirtileri nelerdir?"
covid_query = {"query": {"simple_query_string": {"query": f"{q}"}}, "size": 10}

elasticsearch_response = client.search(index="covid_documents", body=covid_query)

print(json.dumps(elasticsearch_response, indent=4))
