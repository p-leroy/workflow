# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 13:08:04 2022

@author: PaulLeroy
"""

#%% init

import os

import cc
import lastools

root_ = 'C:/DATA/Loire_totale_automne2019/Loire_S01-01_S01-02_S02-01PART'
traitements = os.path.join(root_, '05-Traitements')
lazC2 = os.path.join(traitements, 'C2/*.laz')
lazC3 = os.path.join(traitements, 'C3/*.laz')
tiles500mC2_dir = os.path.join(traitements, 'C2/tiles500m')
tiles500mC2 = os.path.join(tiles500mC2_dir, '*.laz')

Ncores = 25

#%% lasindex
args = {'i': lazC2,
        'cores': Ncores}
lastools.exe('lasindex', args)

#%% lastile
args = {'i': lazC2,
        'tile_size': 500,
        'buffer': 25,
        'cores': Ncores,
        'odir': tiles500mC2_dir,
        'o': 'C2.laz'}
lastools.exe('lastile', args)

#%% lasground
args = {'i': tiles500mC2,
        'step': 6,
        'nature': None,
        'extra_fine': None,
        'cores': Ncores,
        'compute_height': None,
        'odix': '_g',
        'o': 'laz'}
lastools.exe('lasground', args)

#%% lasclassify

#%% las2las

#%% las2las

#%% lastile

#%% lastile

#%% lasthin

#%% lastile

#%% lasmerge



