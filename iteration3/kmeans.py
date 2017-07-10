#!/usr/bin/python2

import numpy as np

def dic2arr(lod):
    '''
    Return from a list of dictionaries { Label: label, data: array }
    a list of arrays
    '''
    l = []
    for i in lod:
        l.append(np.array(i['data']))
    return np.array(l)


def euclidean_dist(v1, v2):
    # print('euc dist', np.linalg.norm(v1-v2))
    return np.linalg.norm(v1 - v2)


def initialize_centroids(k, dim):
    l = []
    for i in range(k):
        l.append(np.random.rand(dim))
    return l


def assign_to_clusters(points, centroids, k):
    clusters = [[] for i in range(k)]

    for p in points:
        dists = np.array([euclidean_dist(p, c) for c in centroids])
        cluster_nr = np.argmin(dists)
        # print(cluster_nr)
        clusters[cluster_nr].append(p)
    return clusters


def update_centroids(clusters, dim):
    centroids = []
    for cluster in clusters:
        if len(cluster) == 0:
            centroids.append(np.random.rand(dim))
        else:
            c = np.array(cluster)
            # print('cluster' ,c)
            # print('centroid', c.mean(axis=0))
            centroids.append(c.mean(axis=0))
    # for i in range(k):
    #    clusters[i] = np.array(clusters[i])
    #    centroids.append(clusters[i].mean(axis=0))
    # print(centroids)
    return centroids


def kmeans(data, k=2, delta=0.05, max_iterations=3):
    # Convert data to stack
    arr = dic2arr(data)
    dimensions = len(arr[0])
    # Initialize centroids (list of k arrays) with random data
    centroids = initialize_centroids(k, dimensions)
    # print('cent_init', centroids)
    # print(stack[1], centroids[1])
    # print(dimensions)    iteration = 0
    iteration = 0
    found = False

    while found == False or iteration <= max_iterations:
        iteration += 1

        # distances = get_distances(arr, centroids)
        # print(distances)
        clusters = assign_to_clusters(arr, centroids, k)
        # We have a list of lists of np.array
        # Ricalculate Centroids
        centroids_old = centroids
        centroids = update_centroids(clusters, dimensions)
        # Distances between new and old Centroids
        cent_dist = []
        for i in range(k):
            cent_dist.append(np.linalg.norm(centroids[i] - centroids_old[i]))
        cent_dist = np.array(cent_dist)

        # Proof delta
        found = True
        for i in cent_dist:
            if i > delta:
                found = False
                break
    return clusters, centroids


