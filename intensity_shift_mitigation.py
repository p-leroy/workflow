import os

import numpy as np
import matplotlib.pyplot as plt

import cc
import C3_line_cleaning as cleaning

#%%
idir = r'C:\DATA\Brioude_30092021\05-Traitements\C3\intensity_shift_mitigation'
i = os.path.join(idir, 'Brioude_30092021_L011_C3_r_400.sbf')

pc, sf, config = cc.read_sbf(i)
imax_minus_i = sf[:, 9]

histogram = np.histogram(imax_minus_i, bins='auto')

plt.plot(histogram[1][:-1], histogram[0])

plt.hist(sf[:, 9], bins='auto')

level = 83
shift = 103
low = imax_minus_i[(0 < imax_minus_i) & (imax_minus_i < level)]
high = imax_minus_i[(level < imax_minus_i) & (imax_minus_i < 200)] - shift
hist_low = np.histogram(low, bins=256)
hist_high = np.histogram(high, bins=256)
plt.plot(hist_low[1][:-1], hist_low[0], '.-b')
plt.plot(hist_high[1][:-1], hist_high[0], '.-r')

#%% clean lines
lines_dir = r'C:\DATA\Brioude_30092021\05-Traitements\C3\raw'
line001 = os.path.join(lines_dir, 'Brioude_30092021_L001_C3_r.laz')
line011 = os.path.join(lines_dir, 'Brioude_30092021_L011_C3_r.laz')

cleaning.intensity_mitigation(line011)

