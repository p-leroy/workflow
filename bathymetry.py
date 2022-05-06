import logging
import os

import numpy as np

import config_workflow as work

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_seed_from_water_surface(c3_cloud_with_c2c3_dist, water_surface, config):
    # c3_cloud_with_c2c3_dist shall contain C2C3_Z, C2C3 and C2C3_XY scalar fields
    head, tail, root, ext = work.head_tail_root_ext(c3_cloud_with_c2c3_dist)
    odir = os.path.join(head, 'bathymetry')
    os.makedirs(odir, exist_ok=True)
    out = os.path.join(odir, root + f'_bathymetry_seed.bin')

    shift = work.get_shift(config)

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {c3_cloud_with_c2c3_dist}'
    cmd += f' -O {water_surface}'
    cmd += ' -C2C_DIST -SPLIT_XY_Z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_xy + shift} -FILTER_SF 0 5.'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_z + shift} -FILTER_SF MIN -0.2'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z + shift} -FILTER_SF MIN -0.2'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out


def propagate(c3_cloud_with_c2c3_dist, current_bathymetry, config, deepness=-0.2, step=None):
    # c3_cloud_with_c2c3_dist shall contain C2C3_Z, C2C3 and C2C3_XY scalar fields
    head, tail, root, ext = work.head_tail_root_ext(c3_cloud_with_c2c3_dist)
    odir = os.path.join(head, 'bathymetry')
    if step is not None:
        out = os.path.join(odir, root + f'_propagation_step_{step}.bin')
    else:
        out = os.path.join(odir, root + f'_propagation.bin')
    dip = np.tan(1. * np.pi / 180)  # dip 1 degree

    shift = work.get_shift(config)

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {c3_cloud_with_c2c3_dist}'
    cmd += f' -O {current_bathymetry}'
    cmd += ' -C2C_DIST -SPLIT_XY_Z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_xy + shift} -FILTER_SF 0.001 10.'  # keep closest points, no duplicates (i.e. xy = 0)
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_z + shift} -FILTER_SF -0.1 0.1'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z + shift} -FILTER_SF MIN {deepness}'  # consider only points with C3 below C2
    cmd += f' -O {current_bathymetry} -MERGE_CLOUDS' # merge new points with the previous ones
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out


def get_bathymetry_hd(line, water_surface, i_c2c_z, globalShift):

    logger.info(f'processing line {line}')

    head, tail, root, ext = work.head_tail_root_ext(line)
    odir = os.path.join(head, 'processing')
    os.makedirs(odir, exist_ok=True)
    out = os.path.join(odir, 'C3_bathymetry_hd.bin')

    x, y, z = globalShift

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O -GLOBAL_SHIFT {x} {y} {z} {line}'
    cmd += f' -O -GLOBAL_SHIFT {x} {y} {z} {water_surface}'
    cmd += ' -C2C_DIST -MAX_DIST 100 -SPLIT_XY_Z'
    cmd += ' -POP_CLOUDS'  # remove water_surface from the database
    cmd += f' -SET_ACTIVE_SF {i_c2c_z} -FILTER_SF MIN -0.2'  # Z keep points which are below the water surface
    cmd += f' -SET_ACTIVE_SF {i_c2c_z + 2} -FILTER_SF MIN 10'  # XY keep points which are close to the water surface
    if os.path.exists(out):
        cmd += f' -O {out} -MERGE_CLOUDS'  # merge new points with the previous ones
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out


def get_bottom_hd(bathymetry_hd, bathymetry):

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O -GLOBAL_SHIFT FIRST {bathymetry_hd}'  # compared
    cmd += f' -O -GLOBAL_SHIFT FIRST {bathymetry}'  # reference
    cmd += ' -C2C_DIST -SPLIT_XY_Z'
    cmd += ' -POP_CLOUDS'
    pass


def get_patches_hd():
    pass
