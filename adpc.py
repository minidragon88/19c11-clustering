# -*- coding: utf-8 -*-
"""adpc.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q5hHpj-scYCAQjhg3oNGBbSJzD9p5kgO

Declaration
"""

import numpy as np
import os
import urllib.request
from sklearn import mixture
from scipy.spatial import distance
import math
import statistics 

CUT_OFF_IN_PERCENT = 0.02

# Clustering data set
# http://cs.joensuu.fi/sipu/datasets/
def download_data_set(file_url = 'http://cs.joensuu.fi/sipu/datasets/s1.txt'):
  local_filename, headers = urllib.request.urlretrieve(url = file_url)
  data = np.loadtxt(local_filename)
  dims = data.shape[1]
  if dims > 2:
    return np.delete(data, 2, 1)
  return data

def gmm_selection(data_set):
  lowest_bic = np.infty
  bic = []
  n_components_range = range(1, min(10, data_set.shape[0]))
  cv_types = ['spherical', 'tied', 'diag', 'full']
  for cv_type in cv_types:
    for n_components in n_components_range:
        # Fit a Gaussian mixture with EM
        gmm = mixture.GaussianMixture(n_components=n_components, covariance_type=cv_type)
        gmm.fit(data_set)
        bic.append(gmm.bic(data_set))
        if bic[-1] < lowest_bic:
            lowest_bic = bic[-1]
            best_gmm = gmm
  # print(best_gmm)
  return best_gmm

# Get all euclid distance between points with keeping their respective order
def get_all_distances(data_set):
  arr_leng = data_set.shape[0]
  all_distances = []
  for i in range(arr_leng):
    current_point_distances = []
    for j in range(arr_leng):
      if i == j:
        continue
      current_point_distances.append(distance.euclidean(data_set[i], data_set[j]))
    all_distances.append(current_point_distances)
  return np.array(all_distances)

def get_cut_off_distance(distances_data):
  arr_leng, dims = distances_data.shape
  # Get number of neighbors
  number_of_items = math.ceil(CUT_OFF_IN_PERCENT * dims)
  all_distances = []
  for i in range(arr_leng):
    point_distance = np.array(distances_data[i])
    # Get number_of_items smallest distance
    point_distance = np.partition(point_distance,number_of_items)[:number_of_items]
    for dist in point_distance:
      all_distances.append(dist)
  return statistics.mean(all_distances) 

def get_density_of_point(point_distance, cut_off_distance):
  arr_leng = len(point_distance)
  result = 0
  for i in range(arr_leng):
    if point_distance[i] < cut_off_distance:
      result += 1
  return result

def get_densities(distances_data, cut_off_distance):
  arr_leng = distances_data.shape[0]
  result = []
  for i in range(arr_leng):
    result.append(get_density_of_point(distances_data[i], cut_off_distance))
  return np.array(result)

def get_distribution(data_set):
  unique, counts = np.unique(data_set, return_counts=True)
  arr_leng = unique.shape[0]
  result = []
  for i in range(arr_leng):
    result.append([unique[i], counts[i]])
  return np.array(result)

def get_density_groups(densities, densities_distribution, groups):
  result = []
  for i in range(len(densities)):
    current_density = densities[i]
    for j in range(len(densities_distribution)):
      if current_density == densities_distribution[j][0]:
        result.append(groups[j])
        break
  return np.array(result)
  
def get_neighbors(all_distances, current_point_index, cut_off_distance):
  neighbor_indexes = []
  neighbor_dinstances = []
  point_distances = all_distances[current_point_index]
  for i in range(len(point_distances)):
    if point_distances[i] < cut_off_distance:
      if i < current_point_index:
        neighbor_indexes.append(i)
      else:
        neighbor_indexes.append(i + 1)
      neighbor_dinstances.append(point_distances[i])
  return (neighbor_indexes, neighbor_dinstances)

def get_index_before_sort(sorted_index, argsort_arr):
  return argsort_arr[sorted_index]

def get_respective_index(index, argsort_arr):
  return argsort_arr[index]

def get_minimum_gaussian_groups(densities_distribution, groups):
  results = []
  for i in range(len(np.unique(groups))):
    results.append(0)
  for i in range(len(densities_distribution)):
    # print(str(groups[i]) + "" + str(densities_distribution[i]))
    group = groups[i]
    results[group] += densities_distribution[i][1]
  return np.where(results == min(results))[0]

"""Download data set"""

# Download data set
raw_data_set = download_data_set('http://cs.joensuu.fi/sipu/datasets/R15.txt')

"""Download data, calculate all relevant variables"""

# calculate all distances
all_distances = get_all_distances(raw_data_set)

# get cut off distance
cut_off_distance = get_cut_off_distance(all_distances)

# calculate densitive base on cut off distance
densities = get_densities(all_distances, cut_off_distance)

# form the distribution to perform gmm selection
densities_distribution = get_distribution(densities)

# get gmm models
gmm_model = gmm_selection(densities_distribution)

# get respective groups
groups = gmm_model.predict(densities_distribution)

# get a respective vector with original densities to represent the desitive of respective point
densities_groups = get_density_groups(densities, densities_distribution, groups)

# Referenced of the original array for futher classification point
densities_argsort = densities.argsort()[::-1]

# Copy to avoid sam referenced then sort in decending order
sorted_densities = np.array(densities)
sorted_densities.sort()
sorted_densities = sorted_densities[::-1]

# Calculate minimum gauss
minimum_gaussian_groups = get_minimum_gaussian_groups(densities_distribution, groups)

# print(all_distances[0])
print(get_neighbors(all_distances, 0, cut_off_distance))
# for i in range(600):
  # print(len(get_neighbors(all_distances, i, cut_off_distance)))
print(raw_data_set[0])
print(densities_distribution)

Algorithm

# sorted_densities cluster_centers = np.append(cluster_centers, 1)
data_set_length = len(raw_data_set)
cluster_centers = []
cluster_centers_label = []
labels = np.zeros((data_set_length,), dtype=np.int)
current_label = 0
# for loop in range(data_set_length):
for loop in range(data_set_length):
  index_in_raw_data = get_respective_index(loop, densities_argsort)
  neighbor_indexes, neighbor_distances = get_neighbors(all_distances, index_in_raw_data, cut_off_distance)
  neighbors_has_clustered = []
  neighbors_has_clustered_distance = []
  neighbors_density_group = []
  for n_count in range(len(neighbor_indexes)):
    neighbor_index_in_sorted = get_respective_index(neighbor_indexes[n_count], densities_argsort)
    if labels[neighbor_index_in_sorted] != 0:
      neighbors_has_clustered.append(neighbor_index_in_sorted)
      neighbors_has_clustered_distance.append(neighbor_distances[n_count])
      neighbors_density_group.append(densities_groups[neighbor_indexes[n_count]])
  # print(neighbors_density_group)
  if len(neighbors_has_clustered) > 0:
    if len(neighbors_has_clustered) == 1:
      labels[loop] = labels[get_respective_index(neighbors_has_clustered[0], densities_argsort)]
    elif len(neighbors_has_clustered) > 1:
      continue
    else:
      # If there are no comparative neighbor's cluster center with the same gaussian group with current point
      # Then get the cluster center of nearest neighbors and belong to that clusters
      decided_cluster = neighbors_has_clustered[neighbors_has_clustered_distance.index(min(neighbors_has_clustered_distance))]
      labels[loop] = labels[decided_cluster]
  elif (not densities_groups[index_in_raw_data] in minimum_gaussian_groups) and sorted_densities[loop] > 0:
    # No neighbor then promote to cluster center
    cluster_centers.append(loop)
    current_label += 1
    # Keep respective cluster label with cluster centers
    cluster_centers_label.append(current_label)
    labels[loop] = current_label
  else:
    # Outlier point, ignore
    continue

print(len(labels))
print(len(cluster_centers))