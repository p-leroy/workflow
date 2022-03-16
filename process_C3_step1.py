import glob
import os

import common_ple as ple

if True:
    root_ = 'G:/RENNES1/PaulLeroy/Brioude_30092021'
else:
    root_ = 'C:/DATA/Brioude_30092021'

traitements = os.path.join(root_, '05-Traitements', 'C3', 'denoised')
i = os.path.join(traitements, '*.laz')
lax = os.path.join(traitements, '*.lax')
dir_tiles = os.path.join(traitements, 'tiles')
tiles = os.path.join(dir_tiles, '*.laz')
tiles_g = os.path.join(dir_tiles, '*_g.laz')
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
ple.exe(f'lasindex -i {i} -cores {cores}')
# build tiles
ple.exe(f'lastile -i {i} -tile_size {tile_size} -buffer {buffer} -cores {cores} -odir {dir_tiles} -o {o}')
# bare-earth extraction: ground points (class = 2) and non-ground points (class = 1)
ple.exe(f'lasground -i {tiles} -step 6 -nature -extra_fine -cores {cores} -odix _g -olaz')
# keep only ground points (class = 2)
ple.exe(f'las2las -i {tiles_g} -keep_class 2 -cores {cores} -odir {dir_tiles} -odix _ground -olaz')
ple.exe(f'lasthin -i {tiles_g} -keep_class 2 -step 1 -lowest -cores {cores} -odix _thin -olaz')

ple.exe(f'lastile -i {tiles_g_thin} -remove_buffer -cores {cores} -olaz')
ple.exe(f'lasmerge -i {tiles_g_thin_1} -o {out}')

remove(lax)
remove(tiles_g)
remove(tiles_g_thin)
remove(tiles_g_thin_1)
