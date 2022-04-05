#import os
#os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE" # alternative => conda install nomkl

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import xsimlab as xs
import fastscape


print('xarray-simlab version: ', xs.__version__)
print('fastscape version: ', fastscape.__version__)

from fastscape.models import basic_model

nx = 101
ny = 101

in_ds = xs.create_setup(
    model=basic_model,
    clocks={
        'time': np.linspace(0., 1e6, 101),
        'out': np.linspace(0., 1e6, 11)
    },
    master_clock='time',
    input_vars={
        'grid__shape': [101, 201],
        'grid__length': [1e4, 2e4],
        'boundary__status': ['looped', 'looped', 'fixed_value', 'fixed_value'],
        'uplift__rate': 1e-3,
        'spl': {'k_coef': 1e-4, 'area_exp': 0.4, 'slope_exp': 1.},
        'diffusion__diffusivity': 1e-1
    },
    output_vars={
        'topography__elevation': 'out',
        'drainage__area': 'out',
        'flow__basin': 'out',
        'spl__chi': None
    }
)

out_ds = in_ds.xsimlab.run(model=basic_model)

