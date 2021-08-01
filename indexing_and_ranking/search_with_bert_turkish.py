import pickle
import pandas as pd
import numpy as np
import time
import faiss
from transformers import AutoModel, AutoTokenizer

model = 'dbmdz-bert-base-turkish-cased'
document_based = True
model_name = model + '_document_based' if document_based else ''


with open(f'./indexing_and_ranking/models/{model}.pkl', 'rb') as input:
    model = pickle.load(input)

tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")

df = pd.read_csv('./indexing_and_ranking/indexes/document_based_index.csv')

index = faiss.read_index(f'./indexing_and_ranking/faiss_indexes/{model_name}.index')


def search_with_bert(query, top_k, index, model, tokenizer):
    inputs = tokenizer(query, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    query_vector = np.array([outputs['pooler_output'].tolist()[0]], dtype='float32')
    top_k = index.search(query_vector, top_k)
    top_k_ids = top_k[1].tolist()[0]
    titles = [df.title[idx] for idx in top_k_ids]
    urls = [df.url[idx] for idx in top_k_ids]
    return titles, urls


titles, urls = search_with_bert("COVID-19'un kaynağı nedir?", 10, index, model, tokenizer)
titles
