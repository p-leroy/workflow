# formerly known as compute_density_on_PC.py (Baptiste Feldmann)

import glob, os

import numpy as np
from scipy.spatial import cKDTree

import plateforme_lidar as pl


def compute_density(points, core_points=[], radius=1, p_norm=2):
    tree = cKDTree(points, leafsize=1000)
    if len(core_points) == 0:
        core_points = np.copy(points)

    return tree.query_ball_point(core_points, r=radius, p=p_norm, return_length=True)


def define_grid(step, sizeX, sizeY, lower_left):
    x0, y0 = lower_left
    tab = []
    for i in range(x0, x0 + sizeX, step):
        for c in range(y0, y0 + sizeY, step):
            tab += [[i + 0.5 * step, c + 0.5 * step]]
    return np.array(tab)


def func(filepath):
    print(f'[density.func] process {filepath}')
    grid_step = 1
    radius = 0.5
    data = pl.lastools.ReadLAS(filepath)
    lower_left = np.int_(np.amin(data.XYZ[:, 0:2], axis=0))
    bbox = np.int_(np.amax(data.XYZ[:, 0:2], axis=0)) - lower_left
    grid = define_grid(grid_step, bbox[0], bbox[1], lower_left)
    result = compute_density(data.XYZ[:, 0:2], grid, radius, np.inf)
    np.savez_compressed(filepath[0:-4] + "_density.npz", result)
    print(f'[density.func] done {filepath}')
