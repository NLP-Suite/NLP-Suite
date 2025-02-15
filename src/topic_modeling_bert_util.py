import matplotlib.pyplot as plt
import GUI_util
import IO_files_util
import re
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic


from sentence_transformers import SentenceTransformer
import pandas as pd
import argparse
import os
from gensim.parsing.preprocessing import STOPWORDS
import json


def get_docs(inputDir, split_docs_var):

    docs = []
    paths = [f_name for f_name in os.listdir(inputDir) if '.txt' in f_name]
    for f_name in paths:
        if split_docs_var == 0:
            with open(f'{inputDir}/{f_name}', 'r', encoding='utf-8') as f:
                docs.append(f.read())
        else:
            chunks = []
            with open(f'{inputDir}/{f_name}', 'r') as f:
                paras = [para for para in f.read().split('\n') if para != '']
            for para in paras:
                chunks += [sentence for sentence in para.split('. ')]
            chunks = [chunk.strip() for chunk in chunks]
            for chunk in chunks:
                d = {
                        'f_name': f_name,
                        'year': f_name.split('_')[0],
                        'text': chunk
                        }
                docs.append(d)

    return docs


def run_BERTopic(inputDir, outputDir, openOutputFiles, split_docs_var):
    
    docs = get_docs(inputDir, split_docs_var)
    if split_docs_var == 1:
        o_path = f'{outputDir}/output'
        if not os.path.exists(o_path):
            os.makedirs(o_path)
        with open(f'{o_path}/chunks.json', 'w') as f:
            json.dump(docs, f)
        docs = [doc['text'] for doc in docs]
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = sentence_model.encode(docs, show_progress_bar=True)
    vectorizer_model = CountVectorizer(stop_words='english')
    topic_model = BERTopic(vectorizer_model=vectorizer_model).fit(docs, embeddings)
    model_path = f'{outputDir}/models'
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'
    topic_model.save(f'{model_path}/model.pt', serialization='pytorch', save_ctfidf=True, save_embedding_model=embedding_model) 
    ####results
    df = topic_model.get_topic_info()
    print(f"Number of documents: {len(docs)}")
    print(f"Documents: {docs[:5]}")
    hierarchical_topics = topic_model.hierarchical_topics(docs)
    fig = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    fig.write_html(f'{outputDir}/topic_hierarchy.html')
    df.to_csv(f'{outputDir}/topic_info.csv')
    filesToOpen = [f'{outputDir}/topic_info.csv', f'{outputDir}/topic_hierarchy.html'] 
    
    return filesToOpen
        

def main():

    inputDir = '/media/gog/external2/data/CGWR Cleaned Feb 20024'
    outputDir = '/home/gog/work/TM-BERTopic_CGWR Cleaned Feb 20024'
    openOutputFiles = 1
    run_BERTopic(inputDir, outputDir, openOutputFiles)


if __name__ == '__main__':
    main()
