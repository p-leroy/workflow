import glob
import os

import config_workflow as work

root_ = 'G:\RENNES1\Vieux_Rhin_2022'
idir = os.path.join(root_, 'processing', 'C3')

i = os.path.join(idir, '*.laz')
lax = os.path.join(idir, '*.lax')
dir_tiles = os.path.join(idir, 'tiles')
dir_tiles_1_2 = os.path.join(idir, 'tiles_1_2')
dir_tiles_1_5_6 = os.path.join(idir, 'tiles_1_5_6')
dir_tiles_2 = os.path.join(idir, 'tiles_2')
tiles = os.path.join(dir_tiles, '*.laz')
tiles_g = os.path.join(dir_tiles_1_2, '*_g.laz')
tiles_gc = os.path.join(dir_tiles_1_2, '*_gc.laz')
tiles_ground = os.path.join(dir_tiles_2, '*_ground.laz')
tiles_ground_1 = os.path.join(dir_tiles_2, '*_ground_1.laz')
tiles_ground_1_thin = os.path.join(dir_tiles_2, '*_ground_1_thin.laz')
tiles_other = os.path.join(dir_tiles_1_5_6, '*_other.laz')
odir = os.path.join(idir, 'processing')
out = os.path.join(odir, 'C3_r_ground_thin_1m.laz')

os.makedirs(dir_tiles, exist_ok=True)  # tiles
os.makedirs(dir_tiles_1_2, exist_ok=True)  # tiles after lasground (classes 1 and 2)
os.makedirs(dir_tiles_1_5_6, exist_ok=True)  # tiles classified after lasclassify (classes 1, 2, 5 and 6)
os.makedirs(dir_tiles_2, exist_ok=True)  # only ground points (class 2)
os.makedirs(odir, exist_ok=True)

buffer = 25
cores = 50
o = 'C3.laz'
tile_size = 500

cpuCount = os.cpu_count()
print(f"cpu_count {cpuCount}")
cores = int((cpuCount / 2))


#%%
# index las files
work.run(f'lasindex -i {i} -cores {cores}')
# build tiles
work.run(f'lastile -i {i} -tile_size {tile_size} -buffer {buffer} -cores {cores} -odir {dir_tiles} -o {o}')

# CLASSIFY
# bare-earth extraction: ground points (class = 2) and non-ground points (class = 1)
work.run(f'lasground -i {tiles} -step 6 -nature -extra_fine -cores {cores} -compute_height -odir {dir_tiles_1_2} -odix _g -olaz')
# classify buildings (class = 6) and high vegetation (class = 5)
work.run(f'lasclassify -i {tiles_g} -cores {cores} -odix c -olaz')

# SEPARATE CLASSES
# keep only ground points (class = 2)
work.run(f'las2las -i {tiles_gc} -keep_class 2 -cores {cores} -odir {dir_tiles_2} -odix _ground -olaz')
# drop ground points (class = 2)
work.run(f'las2las -i {tiles_gc} -drop_class 2 -cores {cores} -odir {dir_tiles_1_5_6} -odix _other -olaz')
# remove buffer (will add _1 to each tile name)
work.run(f'lastile -i {tiles_ground} -remove_buffer -cores {cores} -olaz')
# remove buffer (will add _1 to each tile name)
work.run(f'lastile -i {tiles_other} -remove_buffer -cores {cores} -olaz')

# THIN DATA AND MERGE
work.run(f'lasthin -i {tiles_ground_1} -keep_class 2 -step 1 -lowest -cores {cores} -odix _thin -olaz')
work.run(f'lasmerge -i {tiles_ground_1_thin} -o {out}')

# CLEAN TEMPORARY FILES
work.remove(lax)
os.rmdir(dir_tiles_1_2)
work.remove(tiles_ground)
work.remove(tiles_ground_1_thin)
work.remove(tiles_other)