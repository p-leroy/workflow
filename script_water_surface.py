import os

import water_surface as water
import config_workflow as work

idir = 'C:/DATA/Brioude_30092021/05-Traitements'
# C2 input
c2_config = 'classified'  # values are defined in config_workflow
c2_root = os.path.join(idir, 'C2_r_denoised', 'processing', 'C2_r_ground_thin_1m')
c2_thin = c2_root + '.laz'
# C3 input
c3_config = 'i_corr_classified'  # values are defined in config_workflow
c3_root = os.path.join(idir, 'C3_r_denoised', 'lines_i_correction', 'processing', 'C3_r_ground_thin_1m')
c3_thin = c3_root + '.laz'

#%% COMPUTE C2C DISTANCES BETWEEN C2 AND C3
c2_c2c3 = work.c2c_c2c3(c2_thin, c3_thin, c2_config)
c3_c2c3 = work.c2c_c2c3(c3_thin, c2_thin, c3_config)

#%% EXTRACT WATER SURFACE SEED
water_surface_seed = water.extract_seed(c2_c2c3, c2_config)

#%%
c2_c2c3 = c2_root + '_C2C3.bin'
c3_c2c3 = c3_root + '_C2C3.bin'
water_surface_seed = os.path.join(idir, 'C2_denoised', 'processing', 'water_surface',
                         'C2_thin_lowest_lastOnly_1m_C2C3_water_surface_seed.bin')

#%%
step = 0
water_surface = water.propagate_1deg(c2_c2c3, water_surface_seed, c2_config, step=step)
for step in range(step + 1, step + 10):
    water_surface = water.propagate_1deg(c2_c2c3, water_surface, c2_config, step=step)
