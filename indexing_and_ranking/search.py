import pickle
import pandas as pd
import numpy as np
import time
import faiss

document_based = True
model = 'distilbert-base-multilingual-cased' #'distilbert-base-turkish-cased'
model_name = model + '_document_based' if document_based else ''

with open(f'./indexing_and_ranking/models/{model}.pkl', 'rb') as input:
    model = pickle.load(input)

df = pd.read_csv('./indexing_and_ranking/indexes/document_based_index.csv')

index = faiss.read_index(f'./indexing_and_ranking/faiss_indexes/{model_name}.index')

def search(query, top_k, index, model):
    query_vector = model.encode([query])
    top_k = index.search(query_vector, top_k)
    top_k_ids = top_k[1].tolist()[0]
    titles = [df.title[idx] for idx in top_k_ids]
    urls = [df.url[idx] for idx in top_k_ids]
    return titles, urls

titles, urls = search("biontech mi sinovac mı daha etkili", 5, index, model)