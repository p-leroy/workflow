import glob, os

import bathymetry as bathy
import config_workflow as work

bathymetry_d = r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_denoised\processing\bathymetry'
fwf_d = r'G:\RENNES1\Vieux_Rhin_2022\processing\fwf_without_wdp'
#fwf_d = r'G:\RENNES1\Vieux_Rhin_2022\LAZ-FWF'
class_15 = os.path.join(bathymetry_d, 'bathymetry_cleaned_class_15.laz')
class_15_sbf = os.path.join(bathymetry_d, 'bathymetry_cleaned_class_15.sbf')
fwf_lines = glob.glob(os.path.join(fwf_d, 'c3-2022032*.laz'))
fwf_line_1 = glob.glob(os.path.join(fwf_d, 'c3-20220321-L1-r_w_*.laz'))
fwf_line_1_5 = os.path.join(fwf_d, 'c3-20220321-L1-r_w_5.laz')
fwf_line_1_6 = os.path.join(fwf_d, 'c3-20220321-L1-r_w_6.laz')

#%%
for line in [fwf_line_1_5]:
    bathy.get_fwf_from_class_15_and_depth(line, class_15, work.global_shift_vieux_rhin_fwf)
