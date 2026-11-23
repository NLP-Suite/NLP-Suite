import json
import os
import tkinter.messagebox as mb

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP

import GUI_util

# BERTopic's default min_topic_size: HDBSCAN needs at least this many documents to fit at all
#   (with fewer, BERTopic stops with "k must be less than or equal to the number of training points")
MIN_TOPIC_SIZE = 10


def too_few_documents(n_docs, min_topic_size=MIN_TOPIC_SIZE):
    return n_docs < min_topic_size


# The topics BERTopic found, leaving out -1, the outliers that fit no topic
def topics_found(topic_ids):
    return [topic for topic in topic_ids if topic != -1]


# UMAP starts from a random layout: with a fixed seed the same corpus gives the same topics on every RUN
RANDOM_SEED = 42


def get_docs(inputDir, split_docs_var):

    docs = []
    paths = [f_name for f_name in os.listdir(inputDir) if ".txt" in f_name]
    for f_name in paths:
        if split_docs_var == 0:
            with open(f"{inputDir}/{f_name}", encoding="utf-8") as f:
                docs.append(f.read())
        else:
            chunks = []
            with open(f"{inputDir}/{f_name}") as f:
                paras = [para for para in f.read().split("\n") if para != ""]
            for para in paras:
                chunks += [sentence for sentence in para.split(". ")]
            chunks = [chunk.strip() for chunk in chunks]
            for chunk in chunks:
                d = {"f_name": f_name, "year": f_name.split("_")[0], "text": chunk}
                docs.append(d)

    return docs


def run_BERTopic(inputDir, outputDir, openOutputFiles, split_docs_var):

    docs = get_docs(inputDir, split_docs_var)
    if split_docs_var == 1:
        o_path = f"{outputDir}/output"
        if not os.path.exists(o_path):
            os.makedirs(o_path)
        with open(f"{o_path}/chunks.json", "w") as f:
            json.dump(docs, f)
        docs = [doc["text"] for doc in docs]
    if too_few_documents(len(docs)):
        mb.showwarning(
            title="Too few documents for BERTopic",
            message=f"BERTopic needs at least {MIN_TOPIC_SIZE} documents to find a topic, and your input has "
            f"{len(docs)}.\n\nPlease, add documents or tick 'Split documents into sentences', and try again.",
        )
        return []
    _cache_dir = os.path.join(
        os.path.expanduser("~"), ".cache", "huggingface", "hub", "models--sentence-transformers--all-MiniLM-L6-v2"
    )
    if not os.path.isdir(_cache_dir):
        import IO_user_interface_util

        IO_user_interface_util.timed_alert(
            GUI_util.window,
            6000,
            "BERT model download",
            'Downloading the BERT model "all-MiniLM-L6-v2" for the first time.\n\nThis is a one-time download. Please be patient.',
            False,
        )
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = sentence_model.encode(docs, show_progress_bar=True)
    vectorizer_model = CountVectorizer(stop_words="english")
    # BERTopic's own default UMAP, plus the seed (which also makes UMAP run on one core)
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=RANDOM_SEED)
    topic_model = BERTopic(vectorizer_model=vectorizer_model, umap_model=umap_model, min_topic_size=MIN_TOPIC_SIZE).fit(
        docs, embeddings
    )
    model_path = f"{outputDir}/models"
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    topic_model.save(
        f"{model_path}/model.pt", serialization="pytorch", save_ctfidf=True, save_embedding_model=embedding_model
    )
    ####results
    df = topic_model.get_topic_info()
    print(f"Number of documents: {len(docs)}")
    print(f"Documents: {docs[:5]}")
    df.to_csv(f"{outputDir}/topic_info.csv")
    filesToOpen = [f"{outputDir}/topic_info.csv"]
    # the hierarchy joins topics two by two: with fewer than two, hierarchical_topics stops with
    #   "Found array with 0 sample(s)" (on a small corpus of whole documents every document is an outlier, -1)
    topics = topics_found(df["Topic"])
    if len(topics) < 2:
        mb.showwarning(
            title="BERTopic found too few topics",
            message=f"BERTopic found {len(topics)} topic(s) in your {len(docs)} documents, so there is no topic "
            "hierarchy to chart. Documents that fit no topic are listed as topic -1 in topic_info.csv.\n\n"
            "BERTopic needs many documents. With a small corpus, tick 'Split documents into sentences' and try again.",
        )
        return filesToOpen
    hierarchical_topics = topic_model.hierarchical_topics(docs)
    fig = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    fig.write_html(f"{outputDir}/topic_hierarchy.html")
    filesToOpen.append(f"{outputDir}/topic_hierarchy.html")

    return filesToOpen


def main():

    inputDir = "/media/gog/external2/data/CGWR Cleaned Feb 20024"
    outputDir = "/home/gog/work/TM-BERTopic_CGWR Cleaned Feb 20024"
    openOutputFiles = 1
    run_BERTopic(inputDir, outputDir, openOutputFiles)


if __name__ == "__main__":
    main()
