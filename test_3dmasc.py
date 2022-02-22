# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os

import numpy as np

import cc
import ccConfig as myconfig

#%%
dir_ = "C:/DATA/test_set_classification_field"
l215 = os.path.join(dir_, 'nz10b_cloud.bin')
core = os.path.join(dir_, 'nz10b_raster10.bin')
training_file = os.path.join(dir_, 'params.txt')
globalShift = myconfig.nztm2000_zoneB
spacing = 1
radius = 2

#%%
#core = cc.rasterize(l215, spacing, ext='_RASTER', debug=False, proj='AVG')
res = cc.q3dmasc(l215, training_file, globalShift, core=core, silent=True, debug=True)

#%%
array, shift, config = cc.read_sbf(res)

#%% RESULTS ANALYSIS
rough = array[:, 12]
n = rough.size
nan = np.where(np.isnan(rough))[0]
print(f'{nan.size} / {rough.size} unvalid ({nan.size / n * 100:.2f}%)')

#%% COMPUTE DENSITY
res = cc.density(l215, globalShift, radius, 'SURFACE')
array, shift, config = cc.read_sbf(res)
density = array[:, 3]
