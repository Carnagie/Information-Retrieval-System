from queue import PriorityQueue
from sklearn.metrics.pairwise import cosine_similarity
import torch.nn.functional as F
import torch

def embedding_similarity(query, top_k, embeddings, filtered_ids, doc_ids, fasttext_model):
    query_vector = fasttext_model.get_sentence_vector(query).reshape(1,300)
    q = PriorityQueue()

    current_document_score = -1
    prev_doc = -1
    unique_scores = []
    for psg_id, doc_id in zip(filtered_ids, doc_ids):
        doc_embedding = embeddings[psg_id]
        #score = fastdist.matrix_to_matrix_distance(query_vector, doc_embedding, fastdist.cosine, "cosine")
        score = cosine_similarity(query_vector,doc_embedding.reshape(1,300))[0][0]
        if doc_id == prev_doc:
            if score <= current_document_score:
                continue
            else:
                current_document_score = score
                unique_scores[-1] = (score, psg_id, doc_id)
        else:
            current_document_score = score
            unique_scores.append((score, psg_id, doc_id))
            prev_doc = doc_id

    for score, psg_id, doc_id in unique_scores:
        if q.qsize() < top_k:
            q.put((score, (psg_id,doc_id)))
        elif score > q.queue[0][0]:
            q.get()
            q.put((score, (psg_id,doc_id)))

    q.queue.reverse()
    return q.queue

def pointwise_rerank(query, doc, tokenizer, reranker_model):
    features = tokenizer(query, doc,  max_length=512, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        score = reranker_model(**features).logits
        rank = F.softmax(score, dim=-1)[0,-1].item()

    return rank

def reorder(query, ids, top_k, output_phase, df_passage, df_doc, tokenizer, reranker_model):
    #docs = [df_passage.passage[idx] for idx in ids]
    docs = [df_passage.passage[idx] + " " + df_passage.passage[idx+1] for idx in ids]
    q = PriorityQueue()
    i = 0
    for doc,id in zip(docs,ids):
        score = pointwise_rerank(query,doc, tokenizer, reranker_model)
        if q.qsize() < top_k:
            #q.put((score, id))
            q.put((score,(id, i)))
        elif score > q.queue[0][0]:
            q.get()
            #q.put((score, id))
            q.put((score,(id,i)))
        i += 1

    reordered_list = [q.get() for i in range(q.qsize())]
    reordered_list.reverse()
    if not output_phase:
        return reordered_list

    #docid = [df_passage.docid[idx[1]] for idx in reordered_list]
    docid = [df_passage.docid[idx[1][0]] for idx in reordered_list]
    titles = [df_doc.title[idx] for idx in docid]
    urls = [df_doc.url[idx] for idx in docid]
    #snippet = [df_passage.passage[idx[1]] for idx in reordered_list]
    snippets = [docs[idx[1][1]] for idx in reordered_list]
    #return titles, urls
    return titles, urls, snippets


def bm25(query, index_name, topk, output_phase, client, df_doc):

    covid_query = {"query": {"simple_query_string": {"query": f"{query}"}}, "size": topk}

    elasticsearch_response = client.search(index=index_name, body=covid_query)

    docid = [r['_source']['docid'] for r in elasticsearch_response['hits']['hits']]

    if not output_phase:
        return docid

    titles = [df_doc.title[idx] for idx in docid]
    urls = [df_doc.url[idx] for idx in docid]

    return titles, urls





def three_phase_query(query, hidden_outputs, df_passage, df_doc, embeddings, client, fasttext_model, reranker_model, tokenizer):

    r1 = bm25(query, 'latest_bm25', hidden_outputs[0], False, client=client, df_doc=df_doc)
    filtered_psgs = df_passage[df_passage.docid.isin(r1)].index.to_list()
    doc_ids = df_passage[df_passage.docid.isin(r1)].docid.to_list()

    r2 = embedding_similarity(query, hidden_outputs[1], embeddings, filtered_psgs, doc_ids, fasttext_model)
    psg_ids = [r[1][0] for r in r2]

    r3 = reorder(query, psg_ids, hidden_outputs[2], True, df_passage, df_doc, tokenizer, reranker_model)
    return r3


'''
q = 'Covid-19 belirtileri nelerdir?'
title, url, snippet = three_phase_query(q, [500, 5, 10])


for t,u,s in zip(title, url, snippet):
    print(t)
    print("--------------------------------------------------------------------------------------")
    print(s)
    print("--------------------------------------------------------------------------------------")
    print("\n\n")
'''
'''
#titles_1, urls_1 = bm25(q, 'latest_bm25', False)
r1 = bm25(q, 'latest_bm25', 3, False)
filtered_psgs = df_passage[df_passage.docid.isin(r1)].index.to_list()
doc_ids = df_passage[df_passage.docid.isin(r1)].docid.to_list()

r2 = embedding_similarity(q, 2, embedding, filtered_psgs, doc_ids)
psg_ids = [r[1][0] for r in r2]

r3 = reorder(q,psg_ids, 2, False)
reorder(q,psg_ids, 2, True)

p = [(1,2,3), (4,5,6)]

for a,b,c in p:
    print(a)
'''