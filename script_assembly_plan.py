import glob, os

import assembly_plan as assembly_plan

idir = r'C:\DATA\Brioude_30092021\05-Traitements\C3_denoised_i'

lines = glob.glob(os.path.join(idir, "*.laz"))

assembly_plan.from_lines(lines, idir)
