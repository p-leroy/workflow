import glob, os

import assembly_plan as assembly_plan

idir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C2\tiles'

lines = glob.glob(os.path.join(idir, "L*-1-M01-S1-C2_s.laz"))

date = '202203'

#%% ASSEMBLY PLAN FOR LINES
assembly_plan.from_lines(lines, idir)

#%% ASSEMBLY PLAN FOR TILES
assembly_plan.from_tiles(idir, date)