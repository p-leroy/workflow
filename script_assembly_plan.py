import glob, os

import assembly_plan as assembly_plan

idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C2'

lines = glob.glob(os.path.join(idir, "L*-1-M01-S1-C2_s.laz"))

assembly_plan.from_lines(lines, idir)
