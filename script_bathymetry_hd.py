import os

import bathymetry as bathy

idir = 'C:/DATA/Brioude_30092021/05-Traitements'
lines_dir = os.path.join(idir, 'C3', 'denoised', 'lines_i_correction')
# water surface
water_surface = os.path.join(idir, 'water_surface_merged_withDepth_20220505.las')

lasClassified = False

i_c2c_z = 10

#%%

for i in range(1, 18):
    line = os.path.join(lines_dir, f'Brioude_30092021_L{i:02}_C3_r_denoised_i_corr.laz')
    bathymetry_hd = bathy.get_bathymetry_hd(line, water_surface, i_c2c_z)
