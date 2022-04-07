import os

import bathymetry as bathy

idir = 'C:/DATA/Brioude_30092021/05-Traitements'
c2_c2c = os.path.join(idir, 'C2_ground_thin_1m_C2C.bin')
c3_c2c = os.path.join(idir, 'C3_ground_thin_1m_C2C.bin')

water_surface = os.path.join(idir, 'C2_ground_thin_1m_C2C_propagation_step_9.bin')

if False:
    bathymetry_seed = bathy.extract_seed_from_water_surface(c3_c2c, water_surface)
else:
    bathymetry_seed = os.path.join(idir, 'C3_bathymetry_seed_from_water_surface.bin')

step = 0
bathymetry = bathy.propagate(c3_c2c, bathymetry_seed, step=step)
for step in range(step + 1, step + 11):
    bathymetry = bathy.propagate(c3_c2c, bathymetry, step=step)
