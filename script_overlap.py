import glob, os

from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import numpy as np

import cc
import overlap_map
import overlap_control
import overlap as over
import plateforme_lidar as pl

#%% THIN LINES

#idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C2_r'
idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\03-Calcul_LMS\Brioude\Output'
pattern = '*-1-M01-S1-C3_r.laz'
odir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C3_r'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP MAP C3

workspace = odir
m3c2_params = "m3c2_params.txt"

cc_options = ['standard', 'LAS_auto_save', 'Brioude']
roots_dict = {100: ["L", "-1-M01-S1-C3_s.laz"]}
max_uncertainty = 0.5
max_distance = 10
line_nb_digits = 3
settings = [cc_options, roots_dict, max_uncertainty, max_distance, line_nb_digits]

a = overlap_map.Overlap(workspace, m3c2_params, "L_C3_overlap_map.laz", settings)
a.preprocessing(pattern="*_thin.laz")
overlapping_map = a.processing()
a.clean_temporary_files()

#%% THIN LINES

idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C2_r'
pattern = '*-C2_r.laz'
odir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C2_r_C3_r'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP CONTROL C2

workspace = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap'
m3c2_params = "m3c2_params.txt"
water_surface = "water_surface_merged_withDepth_20220505.las"

cc_options = ['standard', 'LAS_auto_save', "Brioude"]
roots_dict = {100: ["L", "-1-M01-S1-C2_r.laz"]}
max_uncertainty = 0.1
line_nb_digits = 3
settings = [cc_options, roots_dict, max_uncertainty, line_nb_digits]

folder = "C2_r"

a = overlap_control.Overlap(workspace, m3c2_params, water_surface, settings)
a.preprocessing(folder, pattern='*_thin.laz')
a.processing()

#%% OVERLAP CONTROL C3

workspace = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap'
lines_dir_a = r'G:\RENNES1\PaulLeroy\Brioude_30092021\03-Calcul_LMS\Brioude\Output'
cc_options = ['standard', 'LAS_auto_save', "Brioude"]
roots_dict = {100: ["L", "-1-M01-S1-C3_r.laz"]}
max_uncertainty = 0.1
line_nb_digits = 3
settings = [cc_options, roots_dict, max_uncertainty, line_nb_digits]
m3c2_params = "m3c2_params.txt"
water_surface = "water_surface_merged_withDepth_20220505.las"

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)

folder = "C3_r"
a.preprocessing(folder, pattern='*_thin.laz', use_water_surface=False)

a.processing()

#%% OVERLAP CONTROL C2_C3

workspace = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap'
lines_dir_a = r'G:\RENNES1\PaulLeroy\Brioude_30092021\03-Calcul_LMS\Brioude\Output'
lines_dir_b = lines_dir_a
m3c2_params = "m3c2_params.txt"
water_surface = "water_surface_merged_withDepth_20220505.las"

cc_options = ['standard', 'LAS_auto_save', "Brioude"]
line_nb_digits = 3
line_template = ["L", line_nb_digits, "-1-M01-S1-C2_r.laz"]
line_template_b = ["L", line_nb_digits, "-1-M01-S1-C3_r.laz"]
max_uncertainty = 0.1
settings = [cc_options, line_template, max_uncertainty]

folder = "C2_r_C3_r"

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)
a.preprocessing_c2_c3(folder, lines_dir_b, line_template_b)
a.processing()

#%% PLOTS


def func(filepath, distance_filter):
    pc, sf, config = cc.read_sbf(filepath)

    # SF1 = Npoints_cloud1
    # SF2 = Npoints_cloud2
    # SF3 = STD_cloud1
    # SF4 = STD_cloud2
    # SF5 = significant change
    # SF6 = distance uncertainty
    # SF7 = M3C2 distance

    uncertainty = sf[:, 5]
    distance = sf[:, 6]

    select = ~np.isnan(uncertainty)
    select &= (uncertainty < distance_filter)
    select &= ~np.isnan(distance)
    select &= (distance < 1)

    m3c2_dist = distance[select]

    if len(m3c2_dist) > 100:
        line_select = np.unique(np.random.randint(0, len(m3c2_dist), int(0.5 * len(m3c2_dist))))
        results = m3c2_dist[line_select]
    else:
        results = []
    return results


list_filepath = glob.glob(os.path.join(workspace, folder, "*_m3c2_*.sbf"))

if True:
    max_uncertainty = 0.1
    result = Parallel(n_jobs=20, verbose=2)(delayed(func)(i, max_uncertainty) for i in list_filepath)
    np.savez_compressed(os.path.join(workspace, folder, "save_results_data_v1.npz"), np.concatenate(result))

npz = os.path.join(workspace, folder, "save_results_data_v1.npz")
f = np.load(npz)
tab = f[f.files[0]]
f.close()

print(np.mean(tab))
print(np.std(tab))

plt.figure(1)
plt.xlabel("Distance M3C2 (en cm)")
plt.ylabel("Fréquence")
plt.title('Histogramme des écarts en altitude\npour les données du canal vert')
plt.hist(tab * 100, bins=50, range=(-15, 15), edgecolor='white')
plt.ticklabel_format(axis="y", style='sci', scilimits=(0,0))
#plt.text(x=-30,y=3000,s="Moyenne : -9cm\nEcart-type : 5.5cm")
out = os.path.join(workspace, folder,  "figure_C3_v1.png")
plt.savefig(out, dpi=150)
#plt.show()
