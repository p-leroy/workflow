import os

import refraction_correction as corr

idir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_denoised\processing\bathymetry'
bathymetry_laz = os.path.join(idir, 'bathymetry_cleaned_classified.laz')
bathymetry_las = os.path.join(idir, 'bathymetry_cleaned_classified.las')
sbet = os.path.join(idir, 'params_sbet_vieux_rhin_2022.txt')
fwf = False
n_jobs = 1

#%% REFRACTION CORRECTION
corr.do_work(bathymetry_laz, sbet, n_jobs, fwf)
