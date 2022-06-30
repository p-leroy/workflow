import glob, os

import common_ple as ple

idir = r'G:\RENNES1\Vieux_Rhin_2022\LAZ-FWF'
odir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_fwf'

channel = 'c3'
day = 20220321  # 20220321 20220322

line_prefix = f'{channel}-{day}-L'

#%% get the line numbers
line_numbers = []
for basename in glob.glob(os.path.join(idir, f'{line_prefix}*.laz')):
    num = int(basename.split(line_prefix)[-1].split('-')[0])
    if num not in line_numbers:
        line_numbers.append(num)
line_numbers.sort()

#%% for each line, get the numbers of the sublines
sublines_dict = {}
for num in line_numbers:
    sublines_dict[num] = []
    subline_prefix = f'{line_prefix}{num}-r_w_'
    sublines = glob.glob(os.path.join(idir, f'{subline_prefix}*.laz'))
    for subline in sublines:
        sub_num = int(subline.split(subline_prefix)[-1].split('.laz')[0])
        if sub_num not in sublines_dict[num]:
            sublines_dict[num].append(sub_num)

#%% merge sublines to reconstruct lines
for num in line_numbers:
    subline_prefix = f'{line_prefix}{num}-r_'
    o = os.path.join(odir, f'{line_prefix}{num}.laz')
    sublines = os.path.join(idir, f'{subline_prefix}*.laz')
    print(sublines)
    ple.exe(f'lasmerge -i {sublines} -v -o {o}')
