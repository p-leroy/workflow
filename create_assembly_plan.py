# coding: utf-8
# Baptiste Feldmann

import glob, os

import numpy as np
import simplekml
import pyproj
from pyproj import Transformer


dir_ = 'C:/DATA/Brioude_30092021/05-Traitements/C3/tiles500m'
date = "19/10/2020"
rootname = "Loire_19102020_RTemus"

scale = 1000
coords_loc = 1

paths = glob.glob(os.path.join(dir_, "*.laz"))    
names = [os.path.splitext(os.path.split(path)[-1])[0] for path in paths]

plan = simplekml.Kml()

for name in [names[0]]:
    coord = np.int_(name.split("_")[coords_loc : coords_loc + 2])
    coords_line = np.array([[coord[0], coord[1]],
                            [coord[0], coord[1] + scale],
                            [coord[0] + scale, coord[1] + scale],
                            [coord[0] + scale, coord[1]],
                            [coord[0], coord[1]]])
    
    # pyproj 1 style
    p1 = pyproj.Proj(init="epsg:2154")
    p2 = pyproj.Proj(init="epsg:4171")
    tmp = pyproj.transform(p1, p2, coords_line[:,0], coords_line[:,1])
    
    # pyproj 2 style axis order change
    # https://pyproj4.github.io/pyproj/stable/gotchas.html#axis-order-changes-in-proj-6
    # always_xy=True
    transformer = Transformer.from_crs("epsg:2154", "epsg:4171", always_xy=True)
    tmp2 = transformer.transform(coords_line[:,0], coords_line[:,1])
    
    polygon = "dalle_" + "_".join(name.split("_")[coords_loc : coords_loc + 2])
    pol = plan.newpolygon(name=polygon)
    pol.outerboundaryis = [(tmp[0][0],tmp[1][0]),
                           (tmp[0][1],tmp[1][1]),
                           (tmp[0][2],tmp[1][2]),
                           (tmp[0][3],tmp[1][3]),
                           (tmp[0][0],tmp[1][0])]

    pol.style.linestyle.color = simplekml.Color.red
    pol.style.linestyle.scale = 2
    pol.style.linestyle.width = 3
    pol.description = "Date : " + date + "\nCRS : RGF93-Lambert93\nVertical datum : NGF-IGN69\n"
    pol.style.polystyle.color = simplekml.Color.hexa('00000000')

plan.save(os.path.join(dir_, "tableau_assemblage_" + rootname + ".kml"))
