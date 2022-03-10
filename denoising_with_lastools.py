# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 09:07:15 2022

@author: PaulLeroy
"""

import multiprocessing
import os

import lastools
import common_ple as ple

if False:
    idir = r'C:\DATA\Brioude_30092021\05-Traitements\C2'
    odir = r'C:\DATA\Brioude_30092021\05-Traitements\C2\denoised'
else:
    idir = r'C:\DATA\Brioude_30092021\05-Traitements\C3'
    odir = r'C:\DATA\Brioude_30092021\05-Traitements\C3\denoised'

step = 10
isolated = 20

Ncores = multiprocessing.cpu_count()
cores = int(Ncores / 2)

i = os.path.join(idir, "*.laz")

# %% lasnoise step 10 isolated 20 (or 25) remove_noisecore 50 odix _1 olaz
lastools.lasnoise(i, odir, step=step, isolated=isolated, cores=cores)

#%%
ple.exe(f'lasnoise -v -i {i} -remove_noise -step {step} -isolated {isolated} -odir {odir} -odix _denoised -olaz -cores {cores}')