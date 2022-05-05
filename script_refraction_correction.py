import os

import refraction_correction as corr

# define parameters
idir = 'C:/DATA/Brioude_30092021/05-Traitements'
input = os.path.join(idir, 'C3_raw_bathy.laz')
sbet = os.path.join(idir, 'params_sbet_Brioude.txt')
fwf = False
n_jobs= 1

corr.do_work(input, sbet, n_jobs, fwf)
