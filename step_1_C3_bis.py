# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 15:48:02 2022

@author: PaulLeroy
"""

#%% init

import os

import lastools

root_ = 'C:/DATA/Loire_totale_automne2019/Loire_S01-01_S01-02_S02-01PART'
traitements = os.path.join(root_, '05-Traitements')
laz = os.path.join(traitements, 'C3/*.laz')
thin_highest = os.path.join(traitements, 'C3/thin_highest')
out = traitements + '/C3_thin_highest_1m.laz'

Ncores = 25

#%% lasthin
args = {'i': laz,
        'step': 1,
        'highest': None,
        'cores': Ncores,
        'odix': '_thin_highest',
        'odir': thin_highest,
        'olaz': None}
lastools.exe('lasthin', args)

#%% lasmerge
args = {'i': thin_highest + '/*_thin_highest.laz',
        'o': out}
lastools.exe('lasmerge', args)
