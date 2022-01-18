# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 12:50:38 2022

@author: PaulLeroy
"""

#%% init

import os

import lastools

root_ = 'C:/DATA/Loire_totale_automne2019/Loire_S01-01_S01-02_S02-01PART'
traitements = os.path.join(root_, '05-Traitements')
laz = os.path.join(traitements, 'C3/*.laz')
tiles500m = os.path.join(traitements, 'C3/tiles500m')

Ncores = 25

#%% index las files
args = {'i': laz,
        'cores': Ncores}
lastools.exe('lasindex', args)

#%% lastile
args = {'i': laz,
        'tile_size': 500,
        'buffer': 25,
        'cores': Ncores,
        'odir': tiles500m,
        'o': 'C3.laz'}
lastools.exe('lastile', args)

#%% lasground
args = {'i': tiles500m + '/*.laz',
        'step': 6,
        'nature': None,
        'extra_fine': None,
        'cores': Ncores,
        'odix': '_g',
        'olaz': None}
lastools.exe('lasground', args)

#%% keep class 2 to build ground tiles
args = {'i': tiles500m + '/*_g.laz',
        'keep_class': 2,
        'cores': Ncores,
        'odix': '_ground',
        'olaz': None}
lastools.exe('las2las', args)

#%% lasthin
args = {'i': tiles500m + '/*_g.laz',
        'keep_class': 2,
        'step': 1,
        'lowest': None,
        'cores': Ncores,
        'odix': '_thin',
        'olaz': None}
lastools.exe('lasthin', args)

#%% lastile
args = {'i': tiles500m + '/*_g_thin.laz',
        'remove_buffer': None,
        'cores': Ncores,
        'olaz': None}
lastools.exe('lastile', args)

#%% lasmerge
args = {'i': tiles500m + '/*_g_thin_1.laz',
        'o': traitements + '/C3_ground_thin_1m.laz'}
lastools.exe('lasmerge', args)

