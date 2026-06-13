import json
import logging
import os

from bertopic import BERTopic
from model_cache import get_sentence_transformer
from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger(__name__)


def get_docs(inputDir, split_docs_var):
    docs = []
    paths = [f_name for f_name in os.listdir(inputDir) if f_name.endswith(".txt")]
    for f_name in paths:
        file_path = os.path.join(inputDir, f_name)
        if not split_docs_var:
            with open(file_path, encoding="utf-8") as f:
                docs.append(f.read())
        else:
            chunks = []
            with open(file_path, encoding="utf-8") as f:
                paras = [para for para in f.read().split("\n") if para.strip()]
            for para in paras:
                sentences = [sentence.strip() for sentence in para.split(". ")]
                chunks.extend(sentences)
            for chunk in chunks:
                doc_info = {
                    "f_name": f_name,
                    "year": f_name.split("_")[0],
                    "text": chunk,
                }
                docs.append(doc_info)
    return docs


def run_BERTopic(inputDir, outputDir, split_docs_var=False):  # split_docs_var=True
    logger.info("%s %s", inputDir, outputDir)
    # Get documents
    docs = get_docs(inputDir, split_docs_var)

    # If documents are split, save chunks to output directory
    if split_docs_var:
        o_path = os.path.join(outputDir, "output")
        os.makedirs(o_path, exist_ok=True)
        chunks_file = os.path.join(o_path, "chunks.json")
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(docs, f)
        # Extract text from docs for modeling
        docs = [doc["text"] for doc in docs]
    else:
        # If not splitting, docs are already a list of texts
        pass

    # Create embeddings using SentenceTransformer
    sentence_model = get_sentence_transformer("all-MiniLM-L6-v2")
    embeddings = sentence_model.encode(docs, show_progress_bar=True)

    # Initialize BERTopic model
    vectorizer_model = CountVectorizer(stop_words="english")
    topic_model = BERTopic(vectorizer_model=vectorizer_model)

    # Fit the topic model
    topic_model.fit(docs, embeddings)

    # Save the topic model
    model_path = os.path.join(outputDir, "models")
    os.makedirs(model_path, exist_ok=True)
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    model_file = os.path.join(model_path, "model.pt")
    topic_model.save(
        model_file,
        serialization="pytorch",
        save_ctfidf=True,
        save_embedding_model=embedding_model,
    )

    # Generate topic information and hierarchy
    df = topic_model.get_topic_info()
    hierarchical_topics = topic_model.hierarchical_topics(docs)
    fig = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)

    # Save results to the output directory
    hierarchy_file = os.path.join(outputDir, "topic_hierarchy.html")
    fig.write_html(hierarchy_file)
    info_file = os.path.join(outputDir, "topic_info.csv")
    df.to_csv(info_file, index=False)

    # List of files generated to return or further process
    filesToOpen = [info_file, hierarchy_file]

    return filesToOpen
