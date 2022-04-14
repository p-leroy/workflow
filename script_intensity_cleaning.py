import os

import cc
import intensity_cleaning as cleaning

#%% clean lines
lines_dir = r'C:\DATA\Brioude_30092021\05-Traitements\C3\denoised'

#%%
threshold = 83
shift = 103

for i in range(11, 12):
    number = f'{i:03}'
    line = os.path.join(lines_dir, f'Brioude_30092021_L{number}_C3_r_denoised.laz')
    pc_with_imax_minus_i = cleaning.add_sf_imax_minus_i(line)
    cleaning.qc_check(pc_with_imax_minus_i, threshold=threshold, shift=shift)
    sbf = cleaning.correct_intensities_and_add_class(pc_with_imax_minus_i)


#%%

for i in range(1, 18):
    sbf = os.path.join(lines_dir, 'lines_i_correction', f'Brioude_30092021_L{i:03}_C3_r_denoised_i_corr.sbf')
    print(f'[to_laz] {sbf}')
    cc.to_laz(sbf, debug=True)
    #print(f'remove {sbf}')
    #os.remove(sbf)
    #print(f'remove {sbf + ".data"}')
    #os.remove(sbf + '.data')


