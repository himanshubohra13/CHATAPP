import os
import json
from pymilvus import (connections, utility, Collection)
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.milvus import Milvus
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-large')
model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-large')
model.eval()


_HOST = "localhost"
_PORT = "19530"
_INDEX_NAME = "Demo_Index_V1"


embeddings_minilm = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def dict_to_tuple(d):
    if isinstance(d, dict):
        return tuple((k, dict_to_tuple(v)) for k, v in d.items())
    else:
        return d


def process_query(query, top_n = 10, INDEX_NAME = _INDEX_NAME):
    connection_args = {
        "host": _HOST,
        "port": _PORT
    }
    milvus = Milvus(embeddings_minilm, connection_args = connection_args, collection_name = INDEX_NAME)
    ret_docs_mmr = milvus.max_marginal_relevance_search(query, k=top_n)
    ret_docs_sim = milvus.similarity_search_with_score(query, k=top_n)
    ret_docs_mmr_tuples = [(doc.page_content, dict_to_tuple(doc.metadata)) for doc in ret_docs_mmr]
    ret_docs_sim_tuples = [(doc[0].page_content, dict_to_tuple(doc[0].metadata)) for doc in ret_docs_sim]
    combined_tuples = ret_docs_mmr_tuples + ret_docs_sim_tuples
    unique_tuples = set(combined_tuples)
    merged_results = [Document(page_content=content, metadata=dict(metadata)) for content, metadata in unique_tuples]
    return merged_results


def rerank_pairs(query, candidate_responses, top_k=3):
    pairs = [(query, res.page_content) for res in candidate_responses]
    with torch.no_grad():
        inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt')
        scores = model(**inputs, return_dict=True).logits.view(-1).float()
    scores_list = scores.tolist()
    paired_scores = list(zip(candidate_responses, scores_list))
    reranked_results = sorted(paired_scores, key=lambda x: -x[1])
    return reranked_results[:top_k]


def get_results(query, collection_name=_INDEX_NAME):
    query_results = process_query(query=query, INDEX_NAME=collection_name)
    reranked_results = rerank_pairs(query=query, candidate_responses=query_results)

    reranked_results_json = []

    for result, _ in reranked_results:
        result_json = {
            "Patent_Text": result.page_content,
            "Doc_Identifier": result.metadata["Doc_Identifier"],
            "Level": result.metadata["Level"],
            "Assignee": result.metadata["Assignee"],
            "Inventor": result.metadata["Inventor"],
            "Title": result.metadata["Title"],
            "Abstract": result.metadata["Abstract"],
            "First_Claim": result.metadata["First_Claim"]
        }
        reranked_results_json.append(result_json)
    return reranked_results_json