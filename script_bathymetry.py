import os

import bathymetry as bathy

idir = 'C:/DATA/Brioude_30092021/05-Traitements'
# C3 input
c3_config = 'i_corr_not_classified'  # values are defined in config_workflow
c3_c2c3 = os.path.join(idir, 'C3_denoised_i', 'processing', 'C3_thin_lowest_lastOnly_1m_C2C3.bin')
# water surface
water_surface = os.path.join(idir, 'water_surface_cleaned_NN5m-20_smoothed.bin')


#%%
bathymetry_seed = bathy.extract_seed_from_water_surface(c3_c2c3, water_surface, c3_config)

#%%
bathymetry_seed = os.path.join(idir, 'bathymetry', 'C3_bathymetry_seed_from_water_surface.bin')

#%%
step = 0
bathymetry = bathy.propagate(c3_c2c3, bathymetry_seed, c3_config, step=step)
for step in range(step + 1, step + 10):
    bathymetry = bathy.propagate(c3_c2c3, bathymetry, c3_config, step=step)
