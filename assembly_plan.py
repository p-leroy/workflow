# coding: utf-8
# Paul Leroy, Baptiste Feldmann

import glob, logging, os

import numpy as np
import pyproj
import simplekml
from sklearn.decomposition import PCA

import plateforme_lidar as pl

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def transform(coords, epsg_src, epsg_dst):
    # pyproj 2 style axis order change
    # https://pyproj4.github.io/pyproj/stable/gotchas.html#axis-order-changes-in-proj-6
    # always_xy=True
    # 2154 RGF93 / Lambert-93 cartesian 2D
    # 4171 RGF93 ellipsoidal 2D
    transformer = pyproj.Transformer.from_crs(epsg_src, epsg_dst, always_xy=True)
    tmp = transformer.transform(coords[:, 0], coords[:, 1])
    return tmp


def from_tiles(idir, scale=1000, coords_loc=1, epsg_src="epsg:2154", epsg_dst="epsg:4171"):
    tiles = os.path.join(idir, "*.laz")
    paths = glob.glob(tiles)
    names = [os.path.splitext(os.path.split(path)[-1])[0] for path in paths]

    kml = simplekml.Kml()

    for name in names:
        print(name)
        coord = np.int_(name.split("_")[coords_loc : coords_loc + 2])
        coords_tile = np.array([[coord[0], coord[1]],
                                [coord[0], coord[1] + scale],
                                [coord[0] + scale, coord[1] + scale],
                                [coord[0] + scale, coord[1]],
                                [coord[0], coord[1]]])

        tmp = transform(coords_tile, epsg_src, epsg_dst)

        polygon = "tile_" + "_".join(name.split("_")[coords_loc: coords_loc + 2])
        pol = kml.newpolygon(name=polygon)
        pol.outerboundaryis = [(tmp[0][0], tmp[1][0]),
                               (tmp[0][1], tmp[1][1]),
                               (tmp[0][2], tmp[1][2]),
                               (tmp[0][3], tmp[1][3]),
                               (tmp[0][0], tmp[1][0])]

        pol.style.linestyle.color = simplekml.Color.red
        pol.style.linestyle.scale = 2
        pol.style.linestyle.width = 3
        pol.description = "Date : " + date + "\nCRS : RGF93-Lambert93\nVertical datum : NGF-IGN69\n"
        pol.style.polystyle.color = simplekml.Color.hexa('00000000')

    out = os.path.join(idir, "tiles_assembly_plan.kml")
    kml.save(out)

    return out


def from_lines(lines, odir, epsg_src="epsg:2154", epsg_dst="epsg:4171"):
    kml = simplekml.Kml()
    logger.info(f'source EPSG {epsg_src}, destination EPSG {epsg_dst}')
    for line in lines:
        print(line)
        data = pl.lastools.ReadLAS(line)
        pca_pts = PCA(n_components=2, svd_solver='full')
        data_new = pca_pts.fit_transform(data.XYZ[:, 0:2])
        boundaries = np.array([[min(data_new[:, 0]), min(data_new[:, 1])],
                          [min(data_new[:, 0]), max(data_new[:, 1])],
                          [max(data_new[:, 0]), max(data_new[:, 1])],
                          [max(data_new[:, 0]), min(data_new[:, 1])]])
        new_boundaries = pca_pts.inverse_transform(boundaries)

        tmp = transform(new_boundaries, epsg_src, epsg_dst)

        pol = kml.newpolygon(name=line)
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
    kml.save(out)

    return out
