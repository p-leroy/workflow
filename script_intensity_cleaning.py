import os

import cc
import intensity_cleaning as cleaning

#%% clean lines
lines_dir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C3_r_denoised'

#%%
threshold = 83
shift = 102
nb_digits = 3
line_template = ['L', nb_digits, '-1-M01-S1-C3_r_denoised.laz']
for i in range(5, 6):
    name = line_template[0] + str(i).zfill(line_template[1]) + line_template[2]
    line = os.path.join(lines_dir, name)
    pc_with_imax_minus_i = cleaning.add_sf_imax_minus_i(line)
    cleaning.qc_check(pc_with_imax_minus_i, threshold=threshold, shift=shift)
    sbf = cleaning.correct_intensities_and_add_class(pc_with_imax_minus_i)


#%%

for i in range(5, 6):
    laz = line_template[0] + str(i).zfill(line_template[1]) + line_template[2]
    root, ext = os.path.splitext(laz)
    sbf = os.path.join(lines_dir, 'lines_i_correction', root + '_i_corr.sbf')
    print(f'[to_laz] {sbf}')
    cc.to_laz(sbf, debug=True)
    print(f'remove {sbf}')
    os.remove(sbf)
    print(f'remove {sbf + ".data"}')
    os.remove(sbf + '.data')
