import glob, os

from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import numpy as np

import overlap_map
import overlap_control
import overlap as over
import plateforme_lidar as pl

#%% THIN LINES

idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C2_C3'
pattern = '*-1-M01-S1-C2_s.laz'
odir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C2_C3'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP MAP

workspace = odir
params_file = "m3c2_params.txt"

cc_options = ['standard', 'LAS_auto_save', 'Brioude']
roots_dict = {100: ["L", "-1-M01-S1-C3_s.laz"]}
max_uncertainty = 0.5
max_distance = 10
line_nb_digits = 3
settings = [cc_options, roots_dict, max_uncertainty, max_distance, line_nb_digits]

a = overlap_map.Overlap(workspace, params_file, "L_C3_overlap.laz", settings)
a.preprocessing(pattern="*_thin.laz")
overlapping_map = a.processing()
a.clean_temporary_files()

#%% THIN LINES

idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C3'
pattern = '*-C3_s.laz'
odir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C3'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP CONTROL C2_C3

workspace = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap'
params_file = "m3c2_params.txt"
surface_water = "water_surface_merged_withDepth_20220505.las"

cc_options = ['standard', 'LAS_auto_save', "Brioude"]
roots_dict = {100: ["L", "-1-M01-S1-C2_s.laz"]}
max_uncertainty = 0.1
line_nb_digits = 3
settings = [cc_options, roots_dict, max_uncertainty, line_nb_digits]

folder = "C2_C3"

a = overlap_control.Overlap(workspace, params_file, surface_water, settings)
a.preprocessing(folder, pattern='*_thin.laz', c3_pattern='3_s.laz')
a.processing()

#%% PLOTS


def func(filepath, distance_filter):
    data = pl.lastools.ReadLAS(filepath, extraField=True)
    select = ~np.isnan(data["distance__uncertainty"])
    sub_data1 = pl.lastools.Filter_LAS(data, select)
    del data

    select = sub_data1["distance__uncertainty"] < distance_filter
    sub_data2 = pl.lastools.Filter_LAS(sub_data1, select)

    select = ~np.isnan(sub_data2['m3c2__distance'])
    m3c2_dist = sub_data2['m3c2__distance'][select]
    select = np.abs(m3c2_dist) < 1
    m3c2_dist = m3c2_dist[select]

    if len(m3c2_dist) > 100:
        line_select = np.unique(np.random.randint(0, len(m3c2_dist), int(0.5 * len(m3c2_dist))))
        results = m3c2_dist[line_select]
    else:
        results = []
    return results


list_filepath = glob.glob(os.path.join(workspace, folder, "*_m3c2_*.laz"))

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
