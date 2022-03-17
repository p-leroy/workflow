# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 13:08:04 2022

@author: PaulLeroy
"""

# %% init

import glob
import multiprocessing
import os

import common_ple as ple

if True:
    root_ = 'G:/RENNES1/PaulLeroy/Brioude_30092021'
else:
    root_ = 'C:/DATA/Brioude_30092021'

traitements = os.path.join(root_, '05-Traitements', 'C2', 'denoised')
i = os.path.join(traitements, '*.laz')
lax = os.path.join(traitements, '*.lax')
dir_tiles = os.path.join(traitements, 'tiles')
dir_ground = os.path.join(traitements, 'tiles', 'ground')
dir_other = os.path.join(traitements, 'tiles', 'other')
tiles = os.path.join(dir_tiles, '*.laz')
tiles_g = os.path.join(dir_tiles, '*_g.laz')
tiles_gc = os.path.join(dir_tiles, '*_gc.laz')
tiles_ground = os.path.join(dir_ground, '*_ground.laz')
tiles_ground_thin = os.path.join(dir_ground, '*_ground_thin.laz')
tiles_ground_thin_1 = os.path.join(dir_ground, '*_ground_thin_1.laz')
tiles_other = os.path.join(dir_other, '*_other.laz')
out = os.path.join(root_, '05-Traitements', 'C2_ground_thin_1m.laz')

buffer = 25
cores = 50
o = 'C2.laz'
tile_size = 500

cpuCount = multiprocessing.cpu_count()
print(f"cpu_count {cpuCount}")


def create_directories():
    # create directories
    if not os.path.exists(dir_tiles):
        os.makedirs(dir_tiles)
    if not os.path.exists(dir_ground):
        os.makedirs(dir_ground)
    if not os.path.exists(dir_other):
        os.makedirs(dir_other)


def remove(file):
    for f in glob.glob(file):
        os.remove(f)

#%%

create_directories()
# index las files
ple.exe(f'lasindex -i {i} -cores {cores}')
# build tiles
ple.exe(f'lastile -i {i} -tile_size {tile_size} -buffer {buffer} -cores {cores} -odir {dir_tiles} -o {o}')
# bare-earth extraction: ground points (class = 2) and non-ground points (class = 1)
ple.exe(f'lasground -i {tiles} -step 6 -nature -extra_fine -cores {cores} -compute_height -odix _g -olaz')
# classify buildings (class = 6) and high vegetation (class = 5)
ple.exe(f'lasclassify -i {tiles_g} -cores {cores} -odix c -olaz')
# keep only ground points (class = 2)
ple.exe(f'las2las -i {tiles_gc} -keep_class 2 -cores {cores} -odir {dir_ground} -odix _ground -olaz')
# drop ground points (class = 2)
ple.exe(f'las2las -i {tiles_gc} -drop_class 2 -cores {cores} -odir {dir_other} -odix _other -olaz')
# remove buffer (will add _1 to each tile name)
ple.exe(f'lastile -i {tiles_ground} -remove_buffer -cores {cores} -olaz')
# remove buffer (will add _1 to each tile name)
ple.exe(f'lastile -i {tiles_other} -remove_buffer -cores {cores} -olaz')

ple.exe(f'lasthin -i {tiles_ground} -step 1 -lowest -cores {cores} -odix _thin -olaz')
# remove buffer (will add _1 to each tile name)
ple.exe(f'lastile -i {tiles_ground_thin} -remove_buffer -cores {cores} -olaz')
ple.exe(f'lasmerge -i -v {tiles_ground_thin_1} -o {out}')

remove(lax)
remove(tiles_g)
remove(tiles_gc)
remove(tiles_ground_thin)
remove(tiles_ground_thin_1)
