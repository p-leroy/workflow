import glob, os

import assembly_plan as assembly_plan

idir = r'C:\DATA\Brioude_30092021\05-Traitements\tmp'

lines = glob.glob(os.path.join(idir, "*.laz"))

assembly_plan.create(lines, idir)
