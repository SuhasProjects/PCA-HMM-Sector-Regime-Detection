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
    values, vectors = np.linalg.eig(cov_matrix)
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
    return centroids, labels
projected_data = PCA("market_data.csv", False, True)

kmeans_output = kmeans((projected_data), 3)
print(kmeans_output[0])