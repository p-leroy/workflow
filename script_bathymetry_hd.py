import os

import bathymetry as bathy

idir = 'C:/DATA/Brioude_30092021/05-Traitements'
lines_dir = os.path.join(idir, 'C3_denoised_i')
# water surface
water_surface = os.path.join(idir, 'water_surface_merged_withDepth_20220505.las')
# bathymetry thin
bathymetry_thin = os.path.join(idir, 'bathy_cleaned_classified_20220506.las')

lasClassified = False

i_c2c_z = 10
globalShift = (-730000.0, -6470000.0, 0.0)

#%%

for i in range(1, 18):
    line = os.path.join(lines_dir, f'Brioude_30092021_L{i:03}_C3_r_denoised_i_corr.laz')
    bathymetry_hd = bathy.get_bathymetry_hd(line, water_surface, i_c2c_z, globalShift)
