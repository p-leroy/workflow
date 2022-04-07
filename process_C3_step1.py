import glob
import os

import config_workflow as work

if False:
    root_ = 'G:/RENNES1/PaulLeroy/Brioude_30092021'
else:
    root_ = 'C:/DATA/Brioude_30092021'

traitements = os.path.join(root_, '05-Traitements', 'C3', 'denoised')
i = os.path.join(traitements, '*.laz')
lax = os.path.join(traitements, '*.lax')
dir_tiles = os.path.join(traitements, 'tiles')
dir_tiles_g = os.path.join(traitements, 'tiles_g')
dir_tiles_gc = os.path.join(traitements, 'tiles_gc')
dir_tiles_ground = os.path.join(traitements, 'tiles_ground')
tiles = os.path.join(dir_tiles, '*.laz')
tiles_g = os.path.join(dir_tiles_g, '*_g.laz')
tiles_gc = os.path.join(dir_tiles_gc, '*_gc.laz')
tiles_g_thin = os.path.join(dir_tiles, '*_g_thin.laz')
tiles_g_thin_1 = os.path.join(dir_tiles, '*_g_thin_1.laz')
out = os.path.join(root_, '05-Traitements', 'C3_ground_thin_1m.laz')

buffer = 25
cores = 50
o = 'C3.laz'
tile_size = 500

cpuCount = os.cpu_count()
print(f"cpu_count {cpuCount}")


def create_directories():
    # create directories
    if not os.path.exists(dir_tiles):
        os.makedirs(dir_tiles)


def remove(file):
    for f in glob.glob(file):
        os.remove(f)


#%%
create_directories()
# index las files
work.run(f'lasindex -i {i} -cores {cores}')
# build tiles
work.run(f'lastile -i {i} -tile_size {tile_size} -buffer {buffer} -cores {cores} -odir {dir_tiles} -o {o}')
# bare-earth extraction: ground points (class = 2) and non-ground points (class = 1)
work.run(f'lasground -i {tiles} -step 6 -nature -extra_fine -cores {cores} -compute_height -odir {dir_tiles_g} -odix _g -olaz')
# classify buildings (class = 6) and high vegetation (class = 5)
work.run(f'lasclassify -i {tiles_g} -cores {cores} -odir {dir_tiles_gc} -odix c -olaz')
# keep only ground points (class = 2)
work.run(f'las2las -i {tiles_g} -keep_class 2 -cores {cores} -odir {dir_tiles_ground} -odix _ground -olaz')
work.run(f'lasthin -i {tiles_g} -keep_class 2 -step 1 -lowest -cores {cores} -odix _thin -olaz')

work.run(f'lastile -i {tiles_g_thin} -remove_buffer -cores {cores} -olaz')
work.run(f'lasmerge -i {tiles_g_thin_1} -o {out}')

remove(lax)
remove(tiles_g)
remove(tiles_g_thin)
remove(tiles_g_thin_1)
