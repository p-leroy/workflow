# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 10:31:23 2022

@author: PaulLeroy
"""

import glob, os, pickle, time

import plateforme_lidar as pl
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
import numpy as np

#%% define functions
def computeFeatures(workspace, PCX_filename, params_CC, params_features):
    params_training = {"PC1" : "_".join(["PC1"] + PCX_filename.split("_")[1::]),
                       "PCX" : PCX_filename,
                       "CTX" : "_".join(["CTX"] + PCX_filename.split("_")[1::])}
    
    pl.CC_3DMASC.compute_features(params_CC, workspace, params_training, params_features)
    os.rename(workspace + PCX_filename[0:-4] + "_features.sbf", 
              workspace + "features/" + PCX_filename[0:-4] + "_features.sbf")
    os.rename(workspace + PCX_filename[0:-4] + "_features.sbf.data", 
              workspace + "features/" + PCX_filename[0:-4] + "_features.sbf.data")

def CrossValidation(model,cv,X,y_true):
    scores1 = dict(zip(list(np.unique(y_true)) + ['all'],
                       [[] for i in range(0, len(np.unique(y_true)) + 1)]))
    scores2 = dict(zip(list(np.unique(y_true)) + ['all'],
                       [[] for i in range(0, len(np.unique(y_true)) + 1)]))
    feat_import = []
    compt = 1
    print("Cross Validation test with %i folds:" %cv.get_n_splits())
    for train_idx, test_idx in cv.split(X, y_true):
        print(str(compt) + "...", end="\r")
        compt += 1
        model.fit(X[train_idx,:], y_true[train_idx])
        y_pred = model.predict(X[test_idx,:])
        scores1['all'] += [metrics.cohen_kappa_score(y_pred, y_true[test_idx])]
        scores2['all'] += [metrics.accuracy_score(y_true[test_idx], y_pred)]
        feat_import += [model.feature_importances_*100]
        for label in np.unique(y_true):
            scores1[label] += [metrics.cohen_kappa_score(y_pred==label, y_true[test_idx]==label)]
            scores2[label] += [metrics.accuracy_score(y_true[test_idx]==label, y_pred==label)]
    print("done !")
    return scores1, scores2, np.mean(feat_import, axis=0)

#%% LIST FEATURES
# the trailing / is needed here for compliance when defining dir_
dir_ = 'C:/data/training/Loire/juin2019/classif_C3_withSS/dalles/'
features_file = "Loire_20190529_C3_params_v3.txt"
params_CC_0 = ['standard', 'SBF', 'Loire']

list_pcx = [os.path.split(i)[1] for i in glob.glob(os.path.join(dir_, "PCX_*.laz"))]
print("%i files found !" %len(list_pcx))

#%% COMPUTE FEATURES
deb = time.time()
for i in list_pcx:
    print(i + " " + str(list_pcx.index(i) + 1) + "/" + str(len(list_pcx)))
    if not os.path.exists(os.path.join(dir_, "features/" + i[0:-4] + "_features.sbf")):
        computeFeatures(dir_, i, params_CC_0, os.path.join(dir_, features_file))
    print("================================")
print("Time duration: %.1f sec" %(time.time()-deb))

liste_sbf = glob.glob(os.path.join(dir_, "features", "*_features.sbf"))
query = pl.cloudcompare.open_file(params_CC_0, liste_sbf)
pl.cloudcompare.merge_clouds(query)
pl.cloudcompare.last_file(os.path.join(dir_, "features", "*_MERGED_*.sbf"),
                          "PCX_all_features.sbf")
pl.cloudcompare.last_file(os.path.join(dir_, "features", "*_MERGED_*.sbf.data"),
                          "PCX_all_features.sbf.data")

print("Compute features time duration: %.1f sec" %(time.time()-deb))

#%% INITIALISATION
dictio = pl.CC_3DMASC.load_features(
    os.path.join(dir_, "features", "PCX_all_features.sbf"),
    os.path.join(dir_, features_file),
    True)
data = pl.calculs.featureNorm(dictio['features'])
# features normalization :
# NaN are replaced by -1 and for each feature min=0 and max=1
#data=pl.calculs.replace_nan(dictio['features'],0)

names=dictio['names']
labels=dictio['labels']

model = RandomForestClassifier(n_estimators=500, criterion='gini', max_features="auto",
                               max_depth=None, oob_score=True, n_jobs=50, verbose=1)

#%% CROSS VALIDATION
NbFold = 10
deb = time.time()
skf = StratifiedKFold(n_splits=NbFold, shuffle=True, random_state=42)
kappa,OA,feat_import=CrossValidation(model,skf,data,labels)
print("CV time duration: %.1f sec" %(time.time()-deb))
print(kappa,OA,feat_import,sep="\n")

outFile = open(os.path.join(dir_, "test_CrossValidation_3.pkl"), 'wb')
pickle.dump({"kappa":kappa, "OA":OA,"feat_import":feat_import}, outFile)
outFile.close()

#%% TRAINING
model.fit(data,labels)
outFile = open(os.path.join(dir_, "Loire_Rtemus2019_C3_HR_model_v3.pkl"),"wb")
pickle.dump(model,outFile)
outFile.close()

