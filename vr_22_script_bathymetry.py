import os

import bathymetry as bathy

idir = r'G:\RENNES1\Vieux_Rhin_2022\processing'
c3_config = 'not_classified'  # values are defined in config_workflow
c3_c2c3 = os.path.join(idir, 'C3_denoised', 'processing', 'C3_denoised_thin_lowest_lastOnly_1m_C2C3.bin')
# water surface
water_surface = os.path.join(idir, 'step20_cleaned_grad-1_NN5-10_smoothed-5.bin')


#%%
bathymetry_seed = bathy.extract_seed_from_water_surface(c3_c2c3, water_surface, c3_config)

#%%
bathymetry_seed = os.path.join(idir, 'C3_denoised', 'processing',
                               'bathymetry', 'C3_denoised_thin_lowest_lastOnly_1m_C2C3.bin')

#%%
step = 0
bathymetry = bathy.propagate(c3_c2c3, bathymetry_seed, c3_config, step=step)
for step in range(step + 1, step + 21):
    bathymetry = bathy.propagate(c3_c2c3, bathymetry, c3_config, step=step)

