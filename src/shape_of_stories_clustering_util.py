import csv
from tqdm import tqdm
import numpy as np
from scipy.linalg import svd as sp_svd
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import NMF
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt
import os.path
import re #ANGEL

import IO_csv_util
import IO_user_interface_util
import shape_of_stories_vectorizer_util as vec
import shape_of_stories_visualization_util as viz


class SVDClustering:
    def __init__(self, n_modes):
        self.n_modes = n_modes
        return

    @staticmethod
    def reweigh_vecs(vecs, cluster_ids, weights):
        scaled_vectors = []
        for i in range(len(vecs)):
            v = vecs[i]
            cluster_id = cluster_ids[i]
            scaled_v = v / weights[i][cluster_id]
            scaled_vectors.append(scaled_v)

        return get_v_clusters_from_cluster_indices(scaled_vectors, cluster_ids)

    def cluster(self, vectors):
        vectors = np.array(vectors)
        mean_vector = np.array(vectors).mean(axis=1)
        assert mean_vector.shape[0] >= self.n_modes  # the number of modes MUST be <= the vector size!!
        # subtract the feature-wise mean to each of the vector so that each feature has mean 0
        normalized_vecs = np.array(vectors) - np.tile(mean_vector,
                                                      (vectors.shape[1], 1)).transpose()
        # compute svd
        U, s, VT = sp_svd(normalized_vecs)
        # s is a vector containing the coefficients of the max number of modes in VT
        # Sigma = np.zeros((normalized_vecs.shape[0], normalized_vecs.shape[1]))
        # Sigma[:normalized_vecs.shape[1], :normalized_vecs.shape[1]] = np.diag(s)
        # W = np.dot(U, Sigma)  # modes coefficients to "reconstruct" the matrix completely, i.e. using all the modes

        # we can use a shortcut to reconstruct the initial matrix normalized_vecs using a number of components
        # (aka modes) which is less than the number of the original ones.
        w = np.dot(U[:, :self.n_modes], np.diag(s[0:self.n_modes]))
        w_abs = np.abs(w)
        w_normalized = np.multiply(w, np.tile(1. / w_abs.sum(axis=1), (self.n_modes, 1)).transpose())

        pos_modes = VT[:self.n_modes]
        neg_modes = -VT[:self.n_modes]

        # here I (Andrew Reagan) group the normalized vectors since I plot them with the modes which are computed on them,
        # see Appendix E of reference paper. In particular, the legend of fig. S8.
        # Andrew J. Reagan et al. "The emotional arcs of stories are dominated by six basic shapes"
        #
        pos_clusters_indices = np.argmax(w_normalized, axis=-1)
        neg_clusters_indices = np.argmax(-w_normalized, axis=-1)

        # as said in the paper, normalize the vectors by the weights of the modes in W
        pos_vector_clusters = self.reweigh_vecs(normalized_vecs, pos_clusters_indices, w)
        neg_vector_clusters = self.reweigh_vecs(normalized_vecs, neg_clusters_indices, w)
        return pos_vector_clusters, pos_clusters_indices, pos_modes, neg_vector_clusters, neg_clusters_indices, neg_modes

class NMFClustering:
    def __init__(self, n_clusters, max_iter_nmf=1000):
        self.max_iter_nmf = max_iter_nmf
        self.n_clusters = n_clusters

    @staticmethod
    def group_elements(H):
        cluster_ids = []
        for row in range(H.shape[0]):
            best_cl = -1
            best_cl_v = -1
            for col in range(H.shape[1]):
                if H[row][col] > best_cl_v:
                    best_cl = col
                    best_cl_v = H[row][col]
            cluster_ids.append(best_cl)
        return cluster_ids

    def cluster(self, vectors):
        """
        Takes a list of vectors and clusters them.
        :param vectors: a list of real-valued vectors
        :return: a list of lists containing the input vectors grouped into clusters, a
        list of cluster ids of the same shape of the input vectors list. One cluster index per vector.
        """
        assert self.n_clusters >= 1
        assert self.n_clusters < len(vectors)
        model = NMF(n_components=self.n_clusters, init='random', random_state=0, max_iter=self.max_iter_nmf,
                    solver='mu')
        W = model.fit_transform(vectors)
        # H = model.components_.T

        # here the groups are made out of the indices of the docs, not their vectors
        clusters_indices = self.group_elements(W)
        cluster_ids = list(set(clusters_indices))
        # groups the vectors in their respective clusters
        vector_clusters = [[] for _ in range(cluster_ids[0], cluster_ids[len(cluster_ids)-1]+1)]
        for i in range(len(vectors)):
            cluster_idx = clusters_indices[i]
            vector_clusters[cluster_idx].append(vectors[i])
        return vector_clusters, clusters_indices, vectors


class Clustering:
    def __init__(self, n_clust, clustering_alg='ward'):
        # self.dist_thr = dist_thr
        self.n_clust = n_clust
        self.clustering_alg = clustering_alg

    def get_distances(self, X, model, mode='max'):
        distances = []
        weights = []
        children = model.children_
        dims = (X.shape[1], 1)
        distCache = {}
        weightCache = {}
        for childs in children:
            c1 = X[childs[0]].reshape(dims)
            c2 = X[childs[1]].reshape(dims)
            c1Dist = 0
            c1W = 1
            c2Dist = 0
            c2W = 1
            if childs[0] in distCache.keys():
                c1Dist = distCache[childs[0]]
                c1W = weightCache[childs[0]]
            if childs[1] in distCache.keys():
                c2Dist = distCache[childs[1]]
                c2W = weightCache[childs[1]]
            d = np.linalg.norm(c1 - c2)
            cc = ((c1W * c1) + (c2W * c2)) / (c1W + c2W)

            X = np.vstack((X, cc.T))

            newChild_id = X.shape[0] - 1

            # How to deal with a higher level cluster merge with lower distance:
            if mode == 'l2':  # Increase the higher level cluster size suing an l2 norm
                added_dist = (c1Dist ** 2 + c2Dist ** 2) ** 0.5
                dNew = (d ** 2 + added_dist ** 2) ** 0.5
            elif mode == 'max':  # If the previrous clusters had higher distance, use that one
                dNew = max(d, c1Dist, c2Dist)
            elif mode == 'actual':  # Plot the actual distance.
                dNew = d

            wNew = (c1W + c2W)
            distCache[newChild_id] = dNew
            weightCache[newChild_id] = wNew

            distances.append(dNew)
            weights.append(wNew)
        return distances, weights

    def cluster(self, vectors, outputDir):
        """
        Takes a list of vectors and clusters them.
        :param vectors: a list of real-valued vectors
        :return: a list of lists containing the input vectors grouped into clusters, a
        list of cluster ids of the same shape of the input vectors list. One cluster index per vector.
        """
        assert self.n_clust >= 1
        assert self.n_clust < len(vectors)
        cluster = AgglomerativeClustering(n_clusters=self.n_clust, affinity='euclidean', linkage = 'ward')
        cluster.fit_predict(vectors)
        clusters_indices = cluster.labels_
        # computes the complete clustering of the vectors
        """
        Z = linkage(vectors, 'ward')
        # computes the index of the cluster for each input vector
        clusters_indices = fcluster(Z, self.dist_thr, criterion='distance')
        """

        # visualize dendrogram
        plt.title('Hierarchical Clustering Dendrogram')
        distance, weight = self.get_distances(vectors, cluster)
        linkage_matrix = np.column_stack([cluster.children_, distance, weight]).astype(float)
        dendrogram(linkage_matrix)
        plt.xlabel("Index of Documents")
        plt.ylabel("Distance")
        DendogramFilename=os.path.join(outputDir, "SOS_HC_dendrogram.png")
        plt.savefig(DendogramFilename)
        plt.close()

        # computes the distinct number of clusters created
        cluster_ids = set(clusters_indices)
        # groups the vectors in their respective clusters
        vector_clusters = [[] for _ in range(len(cluster_ids))]
        for i in range(len(vectors)):
            cluster_idx = clusters_indices[i]
            vector_clusters[cluster_idx].append(vectors[i])
        return DendogramFilename, vector_clusters, clusters_indices, vectors


def get_v_clusters_from_cluster_indices(vectors, clusters_indices):
    cluster_ids = list(set(clusters_indices))
    vector_clusters = [[] for _ in range(cluster_ids[0], cluster_ids[len(cluster_ids)-1]+1)]
    for i in range(len(vectors)):
        cluster_idx = clusters_indices[i]
        vector_clusters[cluster_idx].append(vectors[i])
    return vector_clusters


# return cluster_file. key: cluster ID, value: (document name, sentiment vector)
def processCluster(cluster_indices,scoresFile_list, file_list, sentiment_vectors, rec_n_clusters, outputFile, inputDir):#Angel
    cluster_file = {}
    for i in range(len(cluster_indices)):
        if cluster_indices[i] in cluster_file:
            cluster_file[cluster_indices[i]].append((file_list[i], sentiment_vectors[i]))
        else:
            cluster_file[cluster_indices[i]] = [(file_list[i], sentiment_vectors[i])]
    # write to csv
    with open(outputFile, 'w',newline='', encoding='utf-8',errors='ignore') as csvfile:
        fieldnames = ["Cluster ID", "Sentiment Score File Name", "Original File Name"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in cluster_file.keys():
            # cluster_file may not include all sequential indices
            try:
                documents = cluster_file[i]
            except:
                continue
            for each in documents: #each: (narratiefile, sentiment_vector)
                #===============ANGEL==============
                match=re.search("^=hyperlink", each[0])
                if match:
                    orgFile=IO_csv_util.undressFilenameForCSVHyperlink(each[0])
                else:
                    orgFile=each[0]
                scFile=scoresFile_list[str(each[0])]
                writer.writerow({'Cluster ID': "Cluster " + str(i + 1), "Sentiment Score File Name": IO_csv_util.dressFilenameForCSVHyperlink(scFile), "Original File Name": IO_csv_util.dressFilenameForCSVHyperlink(orgFile)})
    return cluster_file

def update_Ct_St(sample, H, C_t, S_t):
    for i in range(S_t.shape[0]):
        for j in range(S_t.shape[1]):
            if i in sample and j in sample:
                S_t[i][j] += 1

    clusters = []
    for col in range(H.shape[1]):
        docs_in_same_clust = []
        for row in range(H.shape[0]):
            if np.argmax(H[row]) == col:
                docs_in_same_clust.append(sample[row])
        clusters.append(docs_in_same_clust)

    for cluster in clusters:
        for idx_1 in cluster:
            for idx_2 in cluster:
                C_t[idx_1][idx_2] += 1
                if S_t[idx_1][idx_2] == 0:
                    print('ERROR' + '\n')
    return C_t, S_t

def group_elements(H):
    clusters = {}
    for i in range(H.shape[1]):
        clusters[i] = []
    # group elements
    for row in range(H.shape[0]):
        best_cl = -1
        best_cl_v = -1
        for col in range(H.shape[1]):
            if H[row][col] > best_cl_v:
                best_cl = col
                best_cl_v = H[row][col]

        clusters[best_cl].append(row)  # append document indexes in columns of A
    return clusters

def compute_consensus_matrix(Ct_all, St_all):
    C = np.zeros(shape=(Ct_all.shape[0], Ct_all.shape[1]))
    for i in range(Ct_all.shape[0]):
        for j in range(Ct_all.shape[1]):
            c_ij_t = Ct_all[i][j]
            s_ij_t = St_all[i][j]

            if c_ij_t == 0:
                C[i][j] = 0
            else:
                C[i][j] = c_ij_t / s_ij_t
    return C

def compute_dispersion_coeff(consensus_matrix):
    n = consensus_matrix.shape[0]
    sum = 0
    for i in range(n):
        for j in range(n):
            sum += 4 * (consensus_matrix[i][j] - 0.5) ** 2
    return sum / (n ** 2)


def estimate_best_k(document_matrix, output_dir, filesToOpen):
    document_matrix = np.array(document_matrix)
    max_iter_nmf = 2000
    np.random.seed(0)

    # document_matrix, documents_map = load_data()
    A = np.array(document_matrix).T
    t = 50
    sampling_rate = 0.8

    samples = []
    for i in range(t):
        s = []
        for j in range(A.shape[1]):
            if np.random.random() <= sampling_rate:
                s.append(j)
        samples.append(s)

    disp_coeff_by_top_num = {}
    avg_n_empty_clust_by_top_num = {}
    for groups_number in tqdm(range(2, 150)):
        C_t = np.zeros(shape=(len(document_matrix), len(document_matrix)))
        S_t = np.zeros(shape=(len(document_matrix), len(document_matrix)))
        n_empty_clust = 0
        for s in samples:
            tmp_A = []
            for d in s:
                tmp_A.append(A.T[d])

            tmp_A = np.array(tmp_A).T
            model = NMF(n_components=groups_number, init='random', random_state=0, max_iter=max_iter_nmf, solver='mu')
            tmp_W = model.fit_transform(tmp_A)
            tmp_H = model.components_.T

            C_t, S_t = update_Ct_St(s, tmp_H, C_t, S_t)
            groups = group_elements(tmp_H)
            for g_id, group in groups.items():
                if len(group) == 0:
                    n_empty_clust += 1
        avg_n_empty_clust = n_empty_clust / len(samples)
        avg_n_empty_clust_by_top_num[groups_number] = avg_n_empty_clust
        C_k = compute_consensus_matrix(C_t, S_t)
        disp_coeff = compute_dispersion_coeff(C_k)
        disp_coeff_by_top_num[groups_number] = disp_coeff

    f = open(os.path.join(output_dir, 'best_topic_estimation_stats.csv'), "w", newline='', encoding='utf-8',errors='surrogateescape')
    field_names = ["topic number", "dispersion coefficient", "avg. number of empty clusters over total"]
    writer = csv.DictWriter(f, fieldnames = field_names)
    writer.writeheader()
    x_val = []
    d_coeff_vals = []
    avg_empty_cluster = []
    for t_num, d_coeff in disp_coeff_by_top_num.items():
        x_val.append(t_num)
        d_coeff_vals.append(d_coeff)
        avg_empty_cluster.append(avg_n_empty_clust_by_top_num[t_num] / t_num)
        writer.writerow({"topic number": t_num, "dispersion coefficient": d_coeff, "avg. number of empty clusters over total": avg_n_empty_clust_by_top_num[t_num] / t_num})
    f.close()
    # plot figures
    plt.scatter(x_val, d_coeff_vals, color = "black", s=15)
    plt.title("dispersion coefficient vs topic number")
    plt.savefig(os.path.join(output_dir, 'dispersion coefficient vs topic number.png'))
    filesToOpen.append(os.path.join(output_dir, 'dispersion coefficient vs topic number.png'))
    plt.close()
    plt.scatter(x_val, avg_empty_cluster, color = "black", s=15)
    plt.title("avg. number of empty clusters over total")
    plt.savefig(os.path.join(output_dir, 'avg. number of empty clusters over total.png'))
    filesToOpen.append(os.path.join(output_dir, 'avg. number of empty clusters over total.png'))
    plt.close()
    return filesToOpen

def test():
    sentiment_scores_folder = './data/Sentiment_Health'
    vectz = vec.Vectorizer(sentiment_scores_folder)
    sentiment_vectors = vectz.vectorize()

    # clustering = Clustering(9)
    clustering = NMFClustering(9)
    # clustering = SVDClustering(9)

    grouped_vectors, clusters_indices = clustering.cluster(sentiment_vectors)
    # print('%d clusters' % len(grouped_vectors))
    # print('ok')
    #
    vis = viz.Visualizer('./output')
    vis.visualize_clusters(grouped_vectors)
    exit(0)
    pos_vector_clusters, pos_clusters_indices, pos_modes, neg_vector_clusters, neg_clusters_indices, neg_modes = \
        clustering.cluster(sentiment_vectors)

    vis = viz.Visualizer('./output_pos')
    vis.visualize_clusters(pos_vector_clusters, modes=pos_modes)
    vis = viz.Visualizer('./output_neg')
    vis.visualize_clusters(neg_vector_clusters, modes=neg_modes)



if __name__ == '__main__':
    test()

