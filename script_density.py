import glob, os

import numpy as np
from joblib import Parallel, delayed

import density

#%%
workspace = r'G:\RENNES1\PaulLeroy\Brioude_30092021\04-QC\Overlap\C2'
files = glob.glob(os.path.join(workspace, "*-1-M01-S1-C2_s.laz"))

Parallel(n_jobs=17, verbose=2)(delayed(density.func)(i) for i in files)

all_tab = []
for i in files:
    with np.load(i[0:-4] + "_density.npz") as f:
        tab = f[f.files[0]]
    select = tab > 0
    all_tab += [tab[select]]

all_tab = np.concatenate(all_tab)
print(np.percentile(all_tab, 10))
# [os.remove(i) for i in glob.glob(workspace+"*_density.npz")]