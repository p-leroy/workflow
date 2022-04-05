import glob
import os

import common_ple as ple

if False:
    root_ = 'G:/RENNES1/PaulLeroy/Brioude_30092021'
else:
    root_ = 'C:/DATA/Brioude_30092021'

tiles_in_d = os.path.join(root_, '05-Traitements', 'C3', 'denoised', 'tiles')
tiles_in = os.path.join(tiles_in_d, '*.laz')
tiles_out_d = os.path.join(root_, '05-Traitements', 'C3', 'denoised', 'tiles_lowest')
tiles_out = os.path.join(tiles_out_d, '*.laz')
tiles_out_1 = os.path.join(tiles_out_d, '*_1.laz')
o = os.path.join(root_, '05-Traitements', 'C3_thin_lowest_1m.laz')

buffer = 25
cores = 50
tile_size = 500

cpuCount = os.cpu_count()
print(f"cpu_count {cpuCount}")

ple.exe(f'lasthin -i {tiles_in} -step 1 -lowest -cores {cores} -odir {tiles_out_d} -odix _thin_lastOnly -olaz')
ple.exe(f'lastile -i {tiles_out} -remove_buffer -cores {cores} -olaz')
ple.exe(f'lasmerge -i {tiles_out_1} -o {o}')

# remove temporary files
for f in glob.glob(tiles_out_1):
    os.remove(f)
