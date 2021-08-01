import pickle
import pandas as pd
import numpy as np
import time
import faiss
from flask import Flask

app = Flask(__name__)

df = pd.read_csv('./indexes/document_based_index.csv')


def search(query, top_k, index, model):
    query_vector = model.encode([query])
    top_k = index.search(query_vector, top_k)
    top_k_ids = top_k[1].tolist()[0]
    titles = [df.title[idx] for idx in top_k_ids]
    urls = [df.url[idx] for idx in top_k_ids]
    return titles, urls


@app.route('/', methods=['GET', 'POST'])
def search_query():
    document_based = True
    model = 'distilbert-base-multilingual-cased'  # 'distilbert-base-turkish-cased'
    model_name = model + '_document_based' if document_based else ''

    input = open("./models/" + model + ".pkl", 'rb')
    model = pickle.load(input)

    index = faiss.read_index("./faiss_indexes/" + model_name + ".index")

    titles, urls = search("sinovac mı biontech mi", 5, index, model)

    print(titles, urls)

    return "<h1>hi</h1>"


if __name__ == '__main__':
    app.run()
