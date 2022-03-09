# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 09:07:15 2022

@author: PaulLeroy
"""

import multiprocessing
import os

import lastools

idir = r'C:\DATA\Brioude_30092021\05-Traitements\C2'
i = os.path.join(idir, "*.laz")
odir = r'C:\DATA\Brioude_30092021\05-Traitements\C2\denoised'
step = 10
isolated = 20

Ncores = multiprocessing.cpu_count()
cores = int(Ncores / 2)

# %% lasnoise step 10 isolated 20 (or 25) remove_noisecore 50 odix _1 olaz
lastools.lasnoise(i, odir, step=step, isolated=isolated, cores=cores)
