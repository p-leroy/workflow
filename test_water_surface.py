import os

import water_surface as water
import config_workflow as work

idir = 'C:/DATA/Brioude_30092021/05-Traitements'
c2_thin = os.path.join(idir, 'C2_ground_thin_1m.laz')
c3_thin = os.path.join(idir, 'C3_ground_thin_1m.laz')

if False:
    c2_c2c = work.c2c(c2_thin, c3_thin)
    c3_c2c = work.c2c(c3_thin, c2_thin)
    water_surface_seed = water.extract_seed(c2_c2c)
else:
    c2_c2c = os.path.join(idir, 'C2_ground_thin_1m_C2C.bin')
    c3_c2c = os.path.join(idir, 'C3_ground_thin_1m_C2C.bin')
    water_surface_seed = os.path.join(idir, 'C2_water_seed.bin')

step = 0
water_surface = water.propagate_1deg(c2_c2c, water_surface_seed, step=step)
for step in range(step + 1, step + 10):
    water_surface = water.propagate_1deg(c2_c2c, water_surface, step=step)
