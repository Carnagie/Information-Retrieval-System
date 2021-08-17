import pickle
import pandas as pd
import faiss
import fasttext as ft
from transformers import AutoTokenizer#, AutoModelForSequenceClassification
from elasticsearch import Elasticsearch

fasttext_model = ft.load_model('C:\\Users\\dnz_t\\PycharmProjects\\ranking\\cc.tr.300.bin')

df_passage = pd.read_csv('./indexing_and_ranking/indexes/large_passages.csv')
df_doc = pd.read_csv('./indexing_and_ranking/indexes/large_docs.csv')
tokenizer = AutoTokenizer.from_pretrained("amberoad/bert-multilingual-passage-reranking-msmarco")

with open(f'./indexing_and_ranking/models/bert-multilingual-reranker.pkl', 'rb') as input:
    reranker_model = pickle.load(input)

embedding_name = 'large_fasttext_passage_embedding'
with open(f'./indexing_and_ranking/embeddings/{embedding_name}.pkl', 'rb') as input:
    embeddings = pickle.load(input)

client = Elasticsearch("localhost:9200")


from indexing_and_ranking.three_phase_ranking_functions import three_phase_query

query = ['koronavirüsün bulaşma yolları nelerdir?',
         'Covid-19’un belirtileri nelerdir?',
         'Covid-19’a karşı alınması gereken önlemler nelerdir?',
         'Covid-19’a karşı hangi aşılar mevcut?',
         'Koronavirüsün kaynağı nedir?']



for q in query:
    print(f'------------------------ {q} -------------------------------')
    title, url, snippet = three_phase_query(q, [500, 10, 10], df_passage, df_doc, embeddings, client, fasttext_model, reranker_model, tokenizer)

    q_no = 1
    for t, u, s in zip(title, url, snippet):
        print(f'{q_no}: {t} -- {u}')
        print("--------------------------------------------------------------------------------------")
        print(s)
        print("--------------------------------------------------------------------------------------")
        print()
        q_no+=1

    print()
    print('####################################################################################')
    print('####################################################################################')
    print('####################################################################################')
    print()

