# Document-level semantic similarity & clustering via SBERT (sentence-transformers).
# The sentence/document-level complement to word-level Word2Vec and lexical (WordNet/VerbNet/FrameNet) aggregation.
# Wired into semantic_analysis_main.py ('More semantic analyses' dropdown).

import os
import pandas as pd
import tkinter.messagebox as mb

import IO_files_util
import IO_user_interface_util


def document_similarity_clustering(window, inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation):
    """Embed each document with SBERT, compute a document x document cosine-similarity matrix (csv + interactive
    heatmap), and cluster the documents by MEANING (KMeans, k chosen by silhouette). Returns filesToOpen."""
    files = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
    if not files or len(files) < 2:
        mb.showwarning('Semantic similarity',
                       'Document semantic similarity needs at least 2 txt documents.\n\nSelect a corpus (a directory of txt files) in the INPUT/OUTPUT configuration and try again.')
        return []

    startTime = IO_user_interface_util.timed_alert(window, 3000, 'Analysis start',
                                                   'Started running document semantic similarity & clustering (SBERT) at',
                                                   True, '', True, '', False)

    docs, names = [], []
    for f in files:
        try:
            with open(f, encoding='utf-8', errors='ignore') as fh:
                docs.append(fh.read())
            names.append(os.path.basename(f))
        except Exception:
            pass
    if len(docs) < 2:
        mb.showwarning('Semantic similarity', 'Could not read at least 2 documents from the selected corpus.')
        return []

    # --- SBERT embeddings ---
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        model = SentenceTransformer('all-MiniLM-L6-v2')  # small & fast; downloaded once (~80 MB) on first use
        emb = model.encode(docs, show_progress_bar=False)
    except Exception as e:
        mb.showerror('Semantic similarity',
                     "Could not load the SBERT model or compute embeddings:\n\n" + str(e) +
                     "\n\nThis feature needs the 'sentence-transformers' package (bundled with the NLP Suite) and, "
                     "on first use, an internet connection to download the 'all-MiniLM-L6-v2' model.")
        return []

    filesToOpen = []

    # --- similarity matrix: csv + interactive heatmap ---
    sim = cosine_similarity(emb)
    simFile = os.path.join(outputDir, 'NLP_semantic_similarity_matrix.csv')
    pd.DataFrame(sim, index=names, columns=names).round(4).to_csv(simFile, encoding='utf-8')
    filesToOpen.append(simFile)
    try:
        import plotly.express as px
        fig = px.imshow(sim, x=names, y=names, color_continuous_scale='Viridis', aspect='auto',
                        title='Document semantic similarity (SBERT cosine similarity)')
        heatmapFile = os.path.join(outputDir, 'NLP_semantic_similarity_heatmap.html')
        fig.write_html(heatmapFile)
        filesToOpen.append(heatmapFile)
    except Exception:
        pass

    # --- cluster documents by meaning (KMeans; k chosen by silhouette) ---
    try:
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        n = len(docs)
        best = None
        for k in range(2, min(n, 11)):
            labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(emb)
            if len(set(labels)) > 1:
                score = silhouette_score(emb, labels)
                if best is None or score > best[0]:
                    best = (score, k, labels)
        if best is not None:
            clusterFile = os.path.join(outputDir, 'NLP_semantic_clusters.csv')
            pd.DataFrame({'Document': names, 'Cluster': best[2]}).sort_values('Cluster').to_csv(
                clusterFile, index=False, encoding='utf-8')
            filesToOpen.append(clusterFile)
    except Exception:
        pass

    IO_user_interface_util.timed_alert(window, 3000, 'Analysis end',
                                       'Finished running document semantic similarity & clustering at',
                                       True, '', True, startTime)
    return filesToOpen
