import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def PCA(filename, print_components=False, return_proj_data = True):
    data = np.genfromtxt(filename, delimiter=",", dtype=str)
    data_wo_names_str = data[1:,1:]
    ticker_names = data[0, 1:]
    data_wo_names = data_wo_names_str.astype(np.float32)

    #PCA
    mean = np.mean(data_wo_names, axis=0)
    std_dev = np.std(data_wo_names, axis=0)
    data_std = (data_wo_names - mean) / std_dev
    cov_matrix = np.cov(data_std.T)
    values, vectors = np.linalg.eigh(cov_matrix)
    sorted_indices = np.argsort(values)[::-1]
    values_sorted = values[sorted_indices]
    vectors_sorted = vectors[:,sorted_indices]

    pca_components = vectors_sorted[:, :3]
    projected_data = np.dot(data_std, pca_components)


    loadings = pd.DataFrame(
        pca_components,
        index=ticker_names,
        columns=['PC1', 'PC2','PC3']
    )
    if print_components == True:
        print("TOP 5 ASSETS ON PC1 (Overall Market)")
        print(loadings['PC1'].sort_values(ascending=False).head())

        print("\n")
        print("TOP 5 POSITIVE LOADINGS ON PC2 (Utilities vs. Consumer Disc)")

        print(loadings['PC2'].sort_values(ascending=False).head())

        print("\n")
        print("TOP 5 NEGATIVE LOADINGS ON PC2 (SECTOR ROTATION)")
        print(loadings['PC2'].sort_values().head())

        print("\n")
        print("TOP 5 POSITIVE LOADINGS ON PC3 (IT vs. Energy)")

        print(loadings['PC3'].sort_values(ascending=False).head())

        print("\n")
        print("TOP 5 NEGATIVE LOADINGS ON PC3")
        print(loadings['PC3'].sort_values().head())
    if return_proj_data == True:
        return projected_data
    else: 
        return pca_components
def kmeans(X, K, max_iter = 100, tol=1e-5, seed=None):
    if seed is not None:
        np.random.seed(seed)
    T, D = X.shape
    initial_idx = np.random.choice(T, size=K, replace = False)
    centroids = X[initial_idx].copy()
    for iteration in range(max_iter):
        distances = np.sum((X[:, np.newaxis, :] - centroids[np.newaxis, :, :]) **2, axis = 2)
        labels = np.argmin(distances, axis = 1)

        new_centroids = np.zeros_like(centroids)
        for k in range(K):
            cluster_points = X[labels == k]
            if len(cluster_points) > 0:
                new_centroids[k] = cluster_points.mean(axis = 0)
            else:
                new_centroids[k] = X[np.random.choice(T)]
        centroid_shift = np.sum((new_centroids - centroids) ** 2)
        centroids = new_centroids
        if centroid_shift < tol:
            break
    distances = np.sum((X[:, np.newaxis, :] - centroids[np.newaxis, :, :]) ** 2,axis=2)
    labels = np.argmin(distances, axis=1)
    return centroids, labels
def silhouette(projected_data, labels):
    N = len(projected_data)
    silhouette_array = []

    # If there is only one cluster, silhouette is undefined.
    if len(np.unique(labels)) == 1:
        return 0

    for i in range(N):
        cluster_distances = {}

        for j in range(N):
            if j == i:
                continue

            distance = np.linalg.norm(
                projected_data[i] - projected_data[j]
            )

            cluster = labels[j]

            if cluster not in cluster_distances:
                cluster_distances[cluster] = []

            cluster_distances[cluster].append(distance)

        cluster_averages = {}

        for cluster in cluster_distances:
            cluster_averages[cluster] = np.mean(
                cluster_distances[cluster]
            )

        same_cluster = labels[i]

        same_cluster_distances = cluster_distances.get(same_cluster, [])

        if len(same_cluster_distances) == 0:
            silhouette_array.append(0)
            continue

        a_i = np.mean(same_cluster_distances)

        other_cluster_averages = [
            cluster_averages[cluster]
            for cluster in cluster_averages
            if cluster != same_cluster
        ]

        b_i = min(other_cluster_averages)

        denominator = max(a_i, b_i)

        if denominator == 0:
            s_i = 0
        else:
            s_i = (b_i - a_i) / denominator

        silhouette_array.append(s_i)

    return np.mean(silhouette_array)
def best_kmeans(X, K, n_runs=20):
    best_score = -np.inf
    best_centroids = None
    best_labels = None

    for seed in range(n_runs):
        centroids, labels = kmeans(X, K, seed=seed)

        score = silhouette(X, labels)

        if score > best_score:
            best_score = score
            best_centroids = centroids
            best_labels = labels

    return best_centroids, best_labels, best_score

projected_data = PCA("market_data.csv", False, True)

for i in range(1, 11):
    centroids, labels, score = best_kmeans(projected_data, i, 5)
    print("Best silhouette for", i, " clusters is ", score)
