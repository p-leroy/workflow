import os

import cc
import intensity_cleaning as cleaning

#%% clean lines
lines_dir = r'C:\DATA\Brioude_30092021\05-Traitements\C3\denoised'

#%%
line_number = '01'
threshold = 83
shift = 103
line = os.path.join(lines_dir, f'Brioude_30092021_L{line_number}_C3_r_1.laz')
pc_with_imax_minus_i = cleaning.add_sf_imax_minus_i(line)
cleaning.qc_check(pc_with_imax_minus_i, threshold=threshold, shift=shift)
sbf = cleaning.correct_intensities_and_add_class(pc_with_imax_minus_i)


#%%

cc.to_laz(sbf, debug=True)