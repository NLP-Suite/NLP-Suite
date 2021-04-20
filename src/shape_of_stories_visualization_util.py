import os
import os.path

import matplotlib.pyplot as plt
import numpy as np
import math # math comes with Python
from sklearn.decomposition import PCA


import shape_of_stories_clustering_util as cl
import shape_of_stories_vectorizer_util as ve

class Visualizer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    """
    cluster_file: key: cluster ID, value: [(document name, sentiment vector)]
    grouped_vectors: [[cluster 1 vectors], [cluster 2 vectors], ...]
    method: "Single Vector Decomposition Positive (SVDPositive)"
    method_short: "SVDPositive"
    """
    def visualize_clusters(self, numberOfSentimenFiles, grouped_vectors, method, method_short, cluster_file, modes=None):
        titles = []
        file_names = []
        for i in range(len(grouped_vectors)):
            titles.append(method + "\n" + "Cluster " + str(i + 1) + " (N = " + str(len(cluster_file[i])) + "/" + str(numberOfSentimenFiles) + ")")
            file_names.append(method_short + "_cluster_" + str(i + 1))
        for i in range(len(grouped_vectors)):
            cluster_arr = grouped_vectors[i]
            if modes is not None:
                mode = modes[i]
            else:
                mode = None
            self.generate_plot(cluster_arr, titles[i], file_names[i], mode)
            if "SVD" in method_short:
                continue
            self.generate_subplot(cluster_file[i], titles[i], file_names[i])



    def generate_plot(self, cluster, plot_title, file_name, mode=None):
        # create a new figure
        plt.figure()
        # plot each vector in the cluster
        for vector in cluster:
            plt.plot(range(1, len(vector) + 1), vector, c='b', linewidth=0.5)
        # plot mean vector
        if mode is None:
            mode = np.mean(cluster, axis=0)

        plt.plot(range(1, len(cluster[0]) + 1), mode, c='r', linewidth=1)
        plt.title(plot_title, fontsize=12, loc='center')
        plt.savefig(os.path.join(self.output_dir, file_name.replace(' ', '_') + '.png'))
        plt.close()


    def generate_subplot(self, document_vector, plot_title, file_name):
        maxPlotsHorizontally=4
        row = math.ceil(len(document_vector) / maxPlotsHorizontally)
        fig, axes = plt.subplots(nrows=row, ncols=maxPlotsHorizontally, sharex='all', figsize=(15,20))
        fig.suptitle(plot_title)
        for i in range(len(document_vector)):
            document = os.path.basename(document_vector[i][0])
            vector = document_vector[i][1]
            ax = plt.subplot(row, maxPlotsHorizontally, i + 1)
            plt.title(document, fontsize = 8, loc= 'center')
            plt.plot(range(1, len(vector) + 1), vector, color='black')
        # fig.tight_layout()
        plt.savefig(os.path.join(self.output_dir, file_name.replace(' ', '_') + '_subplot.png'))
        plt.close()

def visualize_sentiment_arcs(sent_arcs, output_fig_path, plot_title='Scatter plot of Principal Component Analysis (PCA) of Sentiment Arcs'):
    """
    Creates scatter plot of sentiment arcs
    :param sent_arcs: a list of high-dimensional vectors (> 2)
    :param output_fig_path: path where to save the figure with the scatter plot
    :param plot_title: title of the figure
    :return:
    """
    # create PCA object to reduce size of sentiment arcs to 2

    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(sent_arcs)
    plt.scatter(principal_components[:, 0], principal_components[:, 1], alpha=.5)
    plt.title(plot_title, fontsize=12, loc='center')
    PCAFilename=os.path.join(output_fig_path, 'PCA_sentiment_scores_'+os.path.basename(output_fig_path)+'.png')
    plt.savefig(PCAFilename)  # optional, commment out if you don't wish to save the figure
    # plt.show()  # optional, commment out if you don't wish to see the figure
    # return the saved png filename
    plt.close()
    return PCAFilename

def test():
    sentiment_scores_folder = './data/Sentiment_Health'
    vectz = ve.Vectorizer(sentiment_scores_folder)
    sentiment_vectors = vectz.vectorize()

    clustering = cl.Clustering(3.5)
    outfilename, grouped_vectors, vectors_cluster_ids = clustering.cluster(sentiment_vectors)
    print('%d clusters' % len(grouped_vectors))

    vis = Visualizer('./output')
    vis.visualize_clusters(grouped_vectors)

    print('ok')


if __name__ == '__main__':
    test()
