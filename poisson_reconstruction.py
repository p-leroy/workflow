import glob, os, time

import numpy as np

import plateforme_lidar as pl


def interpolation(workspace, filename, water_surface, params):
    # params = ['tile_size', 'bbox', 'CC', 'interpolation', 'normals']
    deb = time.time()
    print(filename)

    head, tail = os.path.split(filename)
    root, ext = os.path.splitext(tail)
    bbox = np.array(
        root.split(sep="_")[params['bbox']:params['bbox'] + 2] + [params['tile_size']],
        dtype=str
    )
    print(bbox)
    pl.cloudcompare.lastools_clip_tile(filename[0:-4] + "_sample_mesh.laz", bbox)

    query = pl.cloudcompare.open_file(params['CC'],
                                      [filename[0:-4] + "_sample_mesh_1.laz", os.path.join(workspace, water_surface)])
    pl.cloudcompare.c2c_dist(query, True, 10)
    pl.cloudcompare.last_file(filename[0:-4] + "_sample_mesh_1_C2C_DIST_20*.laz",
                              tail[0:-4] + "_sample_mesh_1_C2C.laz")
    temp = pl.cloudcompare.last_file(os.path.join(workspace, water_surface[0:-4] + "_20*.laz"))
    os.remove(temp)
    # data = pl.lastools.ReadLAS(filename[0:-4] + "_sample_mesh_1_C2C.laz", extraField=True)
    # select = data.c2c_absolute_distances < 100 & data.c2c_absolute_distances_z > -10
    # select &= data.c2c_absolute_distances_z < -1
    #
    # os.remove(filename[0:-4] + "_sample_mesh_1_C2C.laz")
    #
    # if any(select):
    #     data_new = pl.lastools.Filter_LAS(data, select)
    #     pl.lastools.WriteLAS(filename[0:-4] + "_sample_mesh_1_1.laz", data_new)
    #
    #     query = pl.cloudcompare.open_file(params['CC'], [filename[0:-4] + "_sample_mesh_1_1.laz", filename])
    #     pl.cloudcompare.c2c_dist(query, False, 10)
    #     pl.cloudcompare.last_file(filename[0:-4] + "_sample_mesh_1_1_C2C_DIST_20*.laz",
    #                               filename[0:-4] + "_sample_mesh_1_1_C2C.laz")
    #     temp = pl.cloudcompare.last_file(filename[0:-4] + "_20*.laz")
    #     os.remove(temp)
    #     data = pl.lastools.ReadLAS(filename[0:-4] + "_sample_mesh_1_1_C2C.laz", extraField=True)
    #     select = np.logical_and(data.c2c_absolute_distances > 0.5,
    #                             data.c2c_absolute_distances < 200)
    #     os.remove(filename[0:-4] + "_sample_mesh_1_1_C2C.laz")
    #     if any(select):
    #         data_new = pl.lastools.Filter_LAS(data, select)
    #         pl.lastools.WriteLAS(filename[0:-4] + "_sample_mesh_step1.laz", data_new)
    #     else:
    #         print("Pas de point")
    #     os.remove(filename[0:-4] + "_sample_mesh_1_1.laz")
    # else:
    #     print("Pas de point")
    # os.remove(filename[0:-4] + "_sample_mesh_1.laz")
    # print("Duration : %.1f sec\n" % (time.time() - deb))


def interp_step2(workspace, filename, surface_water, params):
    # params=['window','CC','interpolation','normals']
    # window=[minX,minY,maxX,maxY]
    deb = time.time()
    print(filename)
    print("==============")
    pl.cloudcompare.compute_normals(workspace + filename, params['normals'])
    pl.cloudcompare.last_file(workspace + filename[0:-4] + "_20*.ply", filename[0:-4] + "_normals.ply")
    pl.cloudcompare.poisson(workspace + filename[0:-4] + "_normals.ply", params['interpolation'])
    pl.cloudcompare.sample_mesh(
        pl.cloudcompare.open_file(params['CC'], workspace + filename[0:-4] + "_normals_mesh.ply"), 5)
    pl.cloudcompare.last_file(workspace + filename[0:-4] + "_normals_mesh_SAMPLED_POINTS_20*.laz",
                              filename[0:-4] + "_sample_mesh.laz")
    pl.cloudcompare.clip_xy(workspace + filename[0:-4] + "_sample_mesh.laz", params['window'])
    os.remove(workspace + filename[0:-4] + "_normals_mesh.ply")
    os.remove(workspace + filename[0:-4] + "_normals.ply")
    os.remove(workspace + filename[0:-4] + "_sample_mesh.laz")

    query = pl.cloudcompare.open_file(params['CC'],
                                      [workspace + filename[0:-4] + "_sample_mesh_1.laz", workspace + surface_water])
    pl.cloudcompare.c2c_dist(query, True, 10)
    pl.cloudcompare.last_file(workspace + filename[0:-4] + "_sample_mesh_1_C2C_DIST_20*.laz",
                              filename[0:-4] + "_sample_mesh_1_C2C.laz")
    temp = pl.cloudcompare.last_file(workspace + surface_water[0:-4] + "_20*.laz")
    os.remove(temp)
    data = pl.lastools.ReadLAS(workspace + filename[0:-4] + "_sample_mesh_1_C2C.laz", extraField=True)
    select = np.logical_and(data.c2c_absolute_distances < 100,
                            np.logical_and(data.c2c_absolute_distances_z > -10, data.c2c_absolute_distances_z < -1))
    os.remove(workspace + filename[0:-4] + "_sample_mesh_1_C2C.laz")
    if any(select):
        data_new = pl.lastools.Filter_LAS(data, select)
        pl.lastools.WriteLAS(workspace + filename[0:-4] + "_sample_mesh_1_1.laz", data_new)

        query = pl.cloudcompare.open_file(params['CC'],
                                          [workspace + filename[0:-4] + "_sample_mesh_1_1.laz", workspace + filename])
        pl.cloudcompare.c2c_dist(query, False, 10)
        pl.cloudcompare.last_file(workspace + filename[0:-4] + "_sample_mesh_1_1_C2C_DIST_20*.laz",
                                  filename[0:-4] + "_sample_mesh_1_1_C2C.laz")
        temp = pl.cloudcompare.last_file(workspace + filename[0:-4] + "_20*.laz")
        os.remove(temp)
        data = pl.lastools.ReadLAS(workspace + filename[0:-4] + "_sample_mesh_1_1_C2C.laz", extraField=True)
        select = np.logical_and(data.c2c_absolute_distances > 0.5,
                                data.c2c_absolute_distances < 200)
        os.remove(workspace + filename[0:-4] + "_sample_mesh_1_1_C2C.laz")
        if any(select):
            data_new = pl.lastools.Filter_LAS(data, select)
            pl.lastools.WriteLAS(workspace + filename[0:-4] + "_sample_mesh_final.laz", data_new)
        else:
            print("Pas de point")
        os.remove(workspace + filename[0:-4] + "_sample_mesh_1_1.laz")
    else:
        print("Pas de point")
    os.remove(workspace + filename[0:-4] + "_sample_mesh_1.laz")
    print("Duration : %.1f sec\n" % (time.time() - deb))


def neighbors_4(coords, tile_size):
    # return XY lower left coordinates of all neighbors in 4-connect
    # coords=[X,Y] lower left
    listCoords = {"left": np.array([coords[0] - tile_size, coords[1]], dtype=int),
                  "up": np.array([coords[0], coords[1] + tile_size], dtype=int),
                  "right": np.array([coords[0] + tile_size, coords[1]], dtype=int),
                  "down": np.array([coords[0], coords[1] - tile_size], dtype=int)}
    return listCoords


def listing_neighbors(listFilenames, params):
    # params=['bbox','tile_size']
    dictio = {}
    for i in listFilenames:
        splitFilename = i[0:-4].split(sep="_")
        coords = np.array(splitFilename[params['bbox']:params['bbox'] + 2], dtype=int)
        listNeigh = neighbors_4(coords, params['tile_size'])
        dictio[i] = dict(zip(listNeigh.keys(), ["", "", "", ""]))
        for c in listNeigh.keys():
            filename = "_".join(
                splitFilename[0:params['bbox']] + [str(listNeigh[c][0]), str(listNeigh[c][1])] + splitFilename[params[
                                                                                                                   'bbox'] + 2::]) + ".laz"
            if filename in listFilenames and filename not in dictio.keys():
                dictio[i][c] = filename
    return dictio


def bbox_edge(coords, params, buffer=0):
    # coords=[X,Y] lower left
    # params=["edge","tile_size","dist"]
    # dictio=[minX,minY,maxX,maxY]
    dictio = {"right": [params['tile_size'] - params["dist"], -buffer, params['tile_size'] + params["dist"],
                        params["tile_size"] + buffer],
              "left": [-params["dist"], -buffer, params["dist"], params["tile_size"] + buffer],
              "up": [-buffer, params['tile_size'] - params["dist"], params['tile_size'] + buffer,
                     params["tile_size"] + params['dist']],
              "down": [-buffer, -params["dist"], params['tile_size'] + buffer, params['dist']]}
    bbox = np.array([coords[0], coords[1], coords[0], coords[1]])
    bbox += np.array(dictio[params['edge']])
    return np.array(bbox, dtype=int)
