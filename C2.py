import glob
import os

import common_ple as ple

if False:
    root_ = 'G:/RENNES1/PaulLeroy/Brioude_30092021'
else:
    root_ = 'C:/DATA/Brioude_30092021'

idir = os.path.join(root_, '05-Traitements', 'C2_denoised')
tiles_in_d = os.path.join(idir, 'tiles')
tiles_in = os.path.join(tiles_in_d, '*.laz')
tiles_out_d = os.path.join(idir, 'tiles_thin_lastOnly')
tiles_out = os.path.join(tiles_out_d, '*.laz')
tiles_out_1 = os.path.join(tiles_out_d, '*_1.laz')
odir = o = os.path.join(idir, 'processing')
o = os.path.join(odir, 'C2_thin_lowest_lastOnly_1m.laz')

buffer = 25
cores = 50
tile_size = 500

cpuCount = os.cpu_count()
print(f"cpu_count {cpuCount}")

os.makedirs(odir, exist_ok=True)  # processing

ple.exe(f'lasthin -i {tiles_in} -step 1 -lowest -last_only -cores {cores} -odir {tiles_out_d} -odix _thin_lastOnly -olaz')
ple.exe(f'lastile -i {tiles_out} -remove_buffer -cores {cores} -olaz')
ple.exe(f'lasmerge -i {tiles_out_1} -o {o}')

# remove temporary files
for f in glob.glob(tiles_out_1):
    os.remove(f)
