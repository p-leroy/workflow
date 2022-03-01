# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 14:24:35 2022

@author: PaulLeroy
"""

import glob, os, time

import numpy as np

import cv2

import plateforme_lidar as pl

#%% LIST FEATURES
# the trailing / is needed here for compliance when defining dir_
dir_ = 'C:/DATA/training/Loire/juin2019/classif_C3_withSS/dalles/'
features_file = "Loire_20190529_C3_params_v3.txt"
params_CC_0 = ['standard', 'SBF', 'Loire']

list_pcx = [os.path.split(i)[1] for i in glob.glob(os.path.join(dir_, "PCX_*.laz"))]
print("%i files found !" %len(list_pcx))

#%% GET DATA FOR CLASSIFICATION
dictio = pl.CC_3DMASC.load_features(
    os.path.join(dir_, "features", "PCX_all_features.sbf"),
    os.path.join(dir_, features_file),
    True)

# features normalization :
# NaN are replaced by -1 and for each feature min=0 and max=1
# data = pl.calculs.replace_nan(dictio['features'], 0)

data = pl.calculs.featureNorm(dictio['features'])

names = dictio['names']
labels = dictio['labels']

#%% OPENCV
n_trees = 50
eps = 0.01

#%% 
rtree = cv2.ml.RTrees_create()
rtree.setMinSampleCount(2)
#rtree.setMaxDepth(10)
criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, n_trees, eps)
rtree.setTermCriteria(criteria)

deb = time.time()
rtree.train(data.astype(np.float32), cv2.ml.ROW_SAMPLE, labels.astype(np.int32))
print("CV time duration: %.1f sec" %(time.time() - deb))

#%% OPENCV_MP
rtreeMP = cv2.ml.RTrees_create()
rtreeMP.setMinSampleCount(2)
#rtree.setMaxDepth(10)
criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, n_trees, eps)
rtreeMP.setTermCriteria(criteria)

deb = time.time()
rtreeMP.train_MP(data.astype(np.float32), cv2.ml.ROW_SAMPLE, labels.astype(np.int32))
print("CV time duration: %.1f sec" %(time.time() - deb))


#%% OPENCV PREDICT
_, y_hat = rtree.predict(data.astype(np.float32))
