import glob
import os

import common_ple as ple

idir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C2_denoised'
outname = 'C2_denoised_thin_lowest_lastOnly_1m.laz'

tiles_in_d = os.path.join(idir, 'tiles')
tiles_in = os.path.join(tiles_in_d, '*.laz')
tiles_out_d = os.path.join(idir, 'tiles_lowest')
tiles_out = os.path.join(tiles_out_d, '*.laz')
tiles_out_1 = os.path.join(tiles_out_d, '*_1.laz')

odir = o = os.path.join(idir, 'processing')
o = os.path.join(odir, outname)

cpuCount = os.cpu_count()
cores = int(cpuCount / 2)
print(f"cpu_count {cpuCount}")

os.makedirs(tiles_out_d, exist_ok=True)  # tiles
os.makedirs(odir, exist_ok=True)  # processing

#%% THIN TILES, REMOVE BUFFERS AND MERGE
ple.exe(f'lasthin -i {tiles_in} -step 1 -lowest -last_only -cores {cores} -odir {tiles_out_d} -odix _thin_lastOnly -olaz')
ple.exe(f'lastile -i {tiles_out} -remove_buffer -cores {cores} -olaz')
ple.exe(f'lasmerge -i {tiles_out_1} -o {o}')

#%% REMOVE TEMPORARY FILES
for f in glob.glob(tiles_out_1):
    os.remove(f)
