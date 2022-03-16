# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 09:07:15 2022

@author: PaulLeroy
"""

import os

import common_ple as ple

dir_ = 'G:/RENNES1/PaulLeroy/Brioude_30092021/05-Traitements'

if False:
    idir = os.path.join(dir_, 'C2')
    odir = os.path.join(dir_, 'C2', 'denoised')
else:
    idir = os.path.join(dir_, 'C3')
    odir = os.path.join(dir_, 'C3', 'denoised')

step = 10
isolated = 20

Ncores = os.cpu_count()
cores = int(Ncores / 2)

i = os.path.join(idir, "*.laz")

#%%
ple.exe(f'lasnoise -v -i {i} -remove_noise -step {step} -isolated {isolated} -odir {odir} -odix _denoised -olaz -cores {cores}')