# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 13:08:04 2022

@author: PaulLeroy
"""

#%% init

import os

import lastools

root_ = 'C:/DATA/Loire_totale_automne2019/Loire_S01-01_S01-02_S02-01PART'
traitements = os.path.join(root_, '05-Traitements')
lazC2 = os.path.join(traitements, 'C2/*.laz')
tiles500mC2 = os.path.join(traitements, 'C2/tiles500m')
tiles500mC2Gnd = os.path.join(traitements, 'C2/tiles500m/ground')
tiles500mC2Other = os.path.join(traitements, 'C2/tiles500m/other')

Ncores = 25

#%% index las files
args = {'i': lazC2,
        'cores': Ncores}
lastools.exe('lasindex', args)

#%% lastile
args = {'i': lazC2,
        'tile_size': 500,
        'buffer': 25,
        'cores': Ncores,
        'odir': tiles500mC2,
        'o': 'C2.laz'}
lastools.exe('lastile', args)

#%% lasground
args = {'i': tiles500mC2 + '/*.laz',
        'step': 6,
        'nature': None,
        'extra_fine': None,
        'cores': Ncores,
        'compute_height': None,
        'odix': '_g',
        'olaz': None}
lastools.exe('lasground', args)

#%% lasclassify
args = {'i': tiles500mC2 + '/*_g.laz',
        'cores': Ncores,
        'odix': 'c',
        'olaz': None}
lastools.exe('lasclassify', args)

#%% keep class 2 to build ground tiles
args = {'i': tiles500mC2 + '/*_gc.laz',
        'keep_class': 2,
        'cores': Ncores,
        'odir': tiles500mC2Gnd,
        'odix': '_ground',
        'olaz': None}
lastools.exe('las2las', args)

#%% drop class 2 to build other tiles
args = {'i': tiles500mC2 + '/*_gc.laz',
        'drop_class': 2,
        'cores': Ncores,
        'odir': tiles500mC2Other,
        'odix': '_other',
        'olaz': None}
lastools.exe('las2las', args)

#%% remove buffer of ground tiles
args = {'i': tiles500mC2Gnd + '/*_ground.laz',
        'remove_buffer': None,
        'cores': Ncores,
        'olaz': None}
lastools.exe('lastile', args)

#%% remove buffer of other tiles
args = {'i': tiles500mC2Other + '/*_other.laz',
        'remove_buffer': None,
        'cores': Ncores,
        'olaz': None}
lastools.exe('lastile', args)

#%% lasthin
args = {'i': tiles500mC2Gnd + '/*_ground.laz',
        'step': 1,
        'lowest': None,
        'cores': Ncores,
        'odix': '_thin',
        'olaz': None}
lastools.exe('lasthin', args)

#%% lastile
args = {'i': tiles500mC2Gnd + '/*_ground_thin.laz',
        'remove_buffer': None,
        'cores': Ncores,
        'olaz': None}
lastools.exe('lastile', args)

#%% lasmerge
args = {'i': tiles500mC2Gnd + '/*_ground_thin_1.laz',
        'o': traitements + '/C2_ground_thin_1m.laz'}
lastools.exe('lasmerge', args)
