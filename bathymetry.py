import os

import numpy as np

import config_workflow as work


def extract_seed(cloud):
    head, tail = os.path.split(cloud)
    odir = os.path.join(head, 'bathymetry')
    if not os.path.exists(odir):
        os.makedirs(odir)
    out = os.path.join(odir, 'C3_bathymetry_seed.bin')

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {cloud}'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z} -FILTER_SF -5 -0.5'
    cmd += ' -COORD_TO_SF Z -SET_ACTIVE_SF LAST -SF_GRAD TRUE -FILTER_SF MIN 0.1'
    cmd += ' -DENSITY 5. -TYPE KNN'
    cmd += f' -SET_ACTIVE_SF {work.i_nn} -FILTER_SF 45 MAX'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out


def extract_seed_from_water_surface(c3_cloud_with_c2c3_dist, water_surface):
    # c3_cloud_with_c2c3_dist shall contain C2C3_Z, C2C3 and C2C3_XY scalar fields
    head, tail = os.path.split(c3_cloud_with_c2c3_dist)
    odir = os.path.join(head, 'bathymetry')
    if not os.path.exists(odir):
        os.makedirs(odir)
    out = os.path.join(head, 'C3_bathymetry_seed_from_water_surface.bin')

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {c3_cloud_with_c2c3_dist}'
    cmd += f' -O {water_surface}'
    cmd += ' -C2C_DIST -SPLIT_XY_z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_xy} -FILTER_SF 0 5.'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_z} -FILTER_SF MIN -0.2'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z} -FILTER_SF MIN -0.2'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out


def propagate(c3_cloud_with_c2c3_dist, current_bathymetry, deepness=-0.2, step=None):
    # c3_cloud_with_c2c3_dist shall contain C2C3_Z, C2C3 and C2C3_XY scalar fields
    head, tail, root, ext = work.head_tail_root_ext(c3_cloud_with_c2c3_dist)
    odir = os.path.join(head, 'bathymetry')
    if step is not None:
        out = os.path.join(odir, root + f'_propagation_step_{step}.bin')
    else:
        out = os.path.join(odir, root + f'_propagation.bin')
    dip = np.tan(1. * np.pi / 180)  # dip 1 degree

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {c3_cloud_with_c2c3_dist}'
    cmd += f' -O {current_bathymetry}'
    cmd += ' -C2C_DIST -SPLIT_XY_z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_xy} -FILTER_SF 0.001 10.'  # keep closest points, no duplicates (i.e. xy = 0)
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_z} -FILTER_SF -0.1 0.1'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z} -FILTER_SF MIN {deepness}'  # consider only points with C3 below C2
    cmd += f' -O {current_bathymetry} -MERGE_CLOUDS' # merge new points with the previous ones
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out
