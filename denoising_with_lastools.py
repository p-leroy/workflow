# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 09:07:15 2022

@author: PaulLeroy
"""

import glob, os

import common_ple as ple

if True:
    idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\03-Calcul_LMS\Brioude\Output'
    pattern = '*-1-M01-S1-C2_r.laz'
    odir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C2_r_denoised'
else:
    idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\03-Calcul_LMS\Brioude\Output'
    pattern = '*-1-M01-S1-C3_r.laz'
    odir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C3_r_denoised'

step = 10
isolated = 20

Ncores = os.cpu_count()
cores = int(Ncores / 2)


#%%
i = os.path.join(idir, pattern)
ple.exe(f'lasnoise -v -i {i} -remove_noise -step {step} -isolated {isolated} -odir {odir} -odix _denoised -olaz -cores {cores}')