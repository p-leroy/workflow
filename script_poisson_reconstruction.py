import glob, os

import numpy as np

import plateforme_lidar as pl
import poisson_reconstruction as poisson

workspace = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C3\tiles_ground'

tiles = glob.glob(os.path.join(workspace, "*_g_ground.laz"))

water_surface = "C2_ground_thin_1m_watersurface_smooth5.laz"

bbox_place = 1  # start at 0, separator="_"
tile_size = 1000
dist_buffer = 250
dist_cut = 50

params_CC = ['standard', 'LAS', 'Loire45-4']

params_normal = {"shiftname": "Loire45-4",
                 "normal_radius": "2",
                 "model": "QUADRIC"}

params_interp = {"bType": "Neumann",
                 "degree": "2",
                 "width": "4",
                 "scale": "2",
                 "samplesPerNode": "5",
                 "pointWeight": "100",
                 "threads": "45",
                 "density": "",
                 "performance": "",
                 "verbose": ""}

#%% STEP 1: Compute Poisson reconstruction for all tiles
for tile in [tiles[0]]:
    poisson.interpolation(workspace, tile, water_surface,
                          {"interpolation": params_interp, "CC": params_CC, "normals": params_normal, "bbox": bbox_place,
                           "tile_size": tile_size}
                          )

#%% For each tile, cut edges when there are neighbor tiles (in 4-connect)
for tile in tiles:
    print(tile)
    root, ext = os.path.splitext(tile)
    if os.path.exists(root + "_sample_mesh_step1.laz"):
        data = pl.lastools.ReadLAS(root + "_sample_mesh_step1.laz")
        splitname = tile[0:-4].split(sep="_")
        coords_LL = [int(splitname[bbox_place]), int(splitname[bbox_place + 1])]
        dictioNeigh = poisson.neighbors_4(coords_LL, tile_size)
        select = np.array([True] * len(data))
        for c in dictioNeigh.keys():
            filename = "_".join(splitname[0:bbox_place] + [str(dictioNeigh[c][0]), str(dictioNeigh[c][1])] + splitname[
                                                                                                             bbox_place + 2::])
            if os.path.exists(workspace + filename + "_sample_mesh_step1.laz"):
                bbox_cut = poisson.bbox_edge(coords_LL, {"edge": c, "tile_size": tile_size, "dist": dist_cut})
                selectX = data.XYZ[:, 0] > bbox_cut[0] & data.XYZ[:, 0] < bbox_cut[2]
                selectY = data.XYZ[:, 1] > bbox_cut[1] & data.XYZ[:, 1] < bbox_cut[3]
                select = select & ~(selectX & selectY)

        if any(select):
            pl.lastools.WriteLAS(workspace + tile[0:-4] + "_sample_mesh_step1cut.laz",
                                 pl.lastools.Filter_LAS(data, select))


#%% STEP 2: Compute Poisson reconstruction for all overlap area
listNeighbors = poisson.listing_neighbors(tiles, {"bbox": bbox_place, "tile_size": tile_size})
for key in listNeighbors.keys():
    print(key)
    if os.path.exists(workspace + key[0:-4] + "_sample_mesh_step1cut.laz"):
        splitname = key[0:-4].split(sep="_")
        coords_LL = np.array([splitname[bbox_place], splitname[bbox_place + 1]], dtype=int)
        for c in listNeighbors[key]:
            if os.path.exists(workspace + listNeighbors[key][c][0:-4] + "_sample_mesh_step1cut.laz"):
                query = "lasmerge -i " + workspace + key + " " + workspace + key[0:-4] + "_sample_mesh_step1cut.laz " + \
                        workspace + listNeighbors[key][c][0:-4] + "_sample_mesh_step1cut.laz -o " + workspace + key[
                                                                                                              0:-4] + "_step2_" + c + ".laz"
                pl.utils.Run(query)
                bbox_cut = np.array(
                    poisson.bbox_edge(coords_LL, {"edge": c, "tile_size": tile_size, "dist": dist_buffer}, dist_buffer),
                    dtype=str)
                query = "las2las -i " + workspace + key[0:-4] + "_step2_" + c + ".laz -keep_xy " + " ".join(
                    bbox_cut) + " -odix cut -olaz"
                pl.utils.Run(query)
                bbox_cut = np.array(poisson.bbox_edge(coords_LL, {"edge": c, "tile_size": tile_size, "dist": dist_cut}),
                                    dtype=str)
                poisson.interp_step2(workspace, key[0:-4] + "_step2_" + c + "cut.laz", water_surface,
                             {"interpolation": params_interp, "CC": params_CC, "normals": params_normal,
                              "window": bbox_cut})

#%% Merge interpolation files rom Step1 and those from Step2 (overlap area)
if not os.path.exists(workspace + "merge"):
    os.mkdir(workspace + "merge")
pl.utils.Run(
    "lasmerge -i " + workspace + "*_sample_mesh_step1cut.laz -o " + workspace + "merge/interpolation_step1cut.laz")
pl.utils.Run(
    "lasmerge -i " + workspace + "*_sample_mesh_final.laz -o " + workspace + "merge/interpolation_step2final.laz")



