import os

import denoise as denoise


c2_idir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C2'
c2_pattern = 'c2-2022032*.laz'
c2_odir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C2_denoised'

c3_idir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C3'
c3_pattern = 'c3-2022032*.laz'
c3_odir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_denoised'

step = 10  # default 4
isolated = 20  # default 5

n_cores = os.cpu_count()
cores = int(n_cores / 2)

#%% DENOISE C3
i = os.path.join(c3_idir, c3_pattern)
denoise.lasnoise(i, c3_odir, cores)

#%% DENOISE C2
i = os.path.join(c2_idir, c2_pattern)
denoise.lasnoise(i, c2_odir, cores)
