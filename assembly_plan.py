# coding: utf-8
# Baptiste Feldmann

import glob, os

import simplekml
import pyproj
from pyproj import Transformer
import numpy as np
from sklearn.decomposition import PCA

import plateforme_lidar as pl


def create(lines, odir, epsg_src="epsg:2154", epsg_dst="epsg:4171"):
    # 2154 RGF93 / Labmbert-93 cartesian 2D
    # 4171 RGF93 ellipsoidal 2D
    plan = simplekml.Kml()
    for line in lines:
        print(line)
        data = pl.lastools.readLAS(line)
        pca_pts = PCA(n_components=2, svd_solver='full')
        data_new = pca_pts.fit_transform(data.XYZ[:, 0:2])
        boundaries = np.array([[min(data_new[:, 0]), min(data_new[:, 1])],
                          [min(data_new[:, 0]), max(data_new[:, 1])],
                          [max(data_new[:, 0]), max(data_new[:, 1])],
                          [max(data_new[:, 0]), min(data_new[:, 1])]])
        new_boundaries = pca_pts.inverse_transform(boundaries)

        transformer = Transformer.from_crs("epsg:2154", "epsg:4171", always_xy=True)
        tmp = transformer.transform(new_boundaries[:, 0], new_boundaries[:, 1])

        pol = plan.newpolygon(name=line)
        pol.outerboundaryis = [(tmp[0][0], tmp[1][0]),
                               (tmp[0][1], tmp[1][1]),
                               (tmp[0][2], tmp[1][2]),
                               (tmp[0][3], tmp[1][3]),
                               (tmp[0][0], tmp[1][0])]

        pol.style.linestyle.color = simplekml.Color.red
        pol.style.linestyle.scale = 2
        pol.style.linestyle.width = 3
        pol.description = "Système planimétrique : RGF93_Lambert93\nSystème altimétrique : NGF-IGN69"
        pol.style.polystyle.color = simplekml.Color.hexa('0055ff80')

    out = os.path.join(odir, "lines_assembly_plan.kml")
    plan.save(out)

    return out
