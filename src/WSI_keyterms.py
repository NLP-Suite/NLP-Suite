import os
import pickle
import itertools
import pandas as pd
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer


def extract_topn_from_vector(feature_names, sorted_items, topn):

    sorted_items = sorted_items[:topn]
    score_vals = []
    feature_vals = []
    for idx, score in sorted_items:
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]

    return results


#https://github.com/matejMartinc/scalable_semantic_shift/blob/a105c8409db0996c99f0df11d40c35017eb3337c/interpretation.py#L85
def sense_keywords(d, o_path, re_pattern='[^a-zA-Z\'\-’ ]', mf_prop=1, topn=10, ngram_range=(1, 2), add_stopwords=None):
    
    regex = re.compile(re_pattern)
    sp = spacy.load('en_core_web_sm')
    stopwords = sp.Defaults.stop_words
    if add_stopwords is not None:
        stopwords = list(stopwords) + add_stopwords
    kw_d = {}
    for w in d:
        senses = sorted([s for s in d[w]])
        clusters = []
        for s in senses:
            doc = ' '.join([sent for sent in d[w][s]]).lower()
            doc = regex.sub('', doc).split()
            clusters.append(doc)
        vocab = list(itertools.chain.from_iterable(clusters))
        v_size = len(set([w for w in vocab if w not in stopwords]))
        clusters = [' '.join(c) for c in clusters]
        tfidf_transformer = TfidfVectorizer(smooth_idf=True, use_idf=True, ngram_range=ngram_range, max_features=int(mf_prop * v_size), stop_words=stopwords)
        tfidf_transformer.fit(clusters)
        feature_names = tfidf_transformer.get_feature_names()
        kw_d[w] = {}
        for i, cluster in enumerate(clusters):
            tf_idf_vector = tfidf_transformer.transform([cluster])
            tuples = zip(tf_idf_vector.tocoo().col, tf_idf_vector.tocoo().data)
            sorted_items = sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)
            keywords = extract_topn_from_vector(feature_names, sorted_items, topn*5)
            keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
            keywords = [x[0] for x in keywords]
            #filter unigrams that appear in ngrams and remove duplicates
            all_ngrams = " ".join([kw for kw in keywords if len(kw.split()) > 1])
            already_in = set()
            filtered_keywords = []
            for kw in keywords:
                if len(kw.split()) < ngram_range[1] and kw in all_ngrams:
                    continue
                elif len(set(kw.split())) < len(kw.split()):
                    continue
                else:
                    if kw not in already_in and kw != w:
                        filtered_keywords.append(kw)
                        already_in.add(kw)
            kw_d[w][i] = filtered_keywords[:topn]

    kw_dfs = {w: pd.DataFrame.from_dict(kw_d[w], orient='index') for w in kw_d}
    kw_df = pd.concat(kw_dfs)
#    print(kw_dfs)    
    if not os.path.exists(o_path):
        os.makedirs(o_path)
    k_path = f'{o_path}/keywords_ngram_range={ngram_range[0]}_{ngram_range[1]}.csv'
    kw_df.to_csv(k_path)
    
    return kw_df, k_path


def get_keyterms(docs, paths, ngram_range=(1, 2), topn=10):
   
    k_paths = []
    for doc in docs:
        i_path = paths[doc]
        with open(f'{i_path}/d.pickle', 'rb') as f:
            d = pickle.load(f)
        _, k_path = sense_keywords(d, i_path, topn=topn, ngram_range=ngram_range)
        k_paths.append(k_path)
    print('\nDone.\n')

    return k_paths
