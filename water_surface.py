import os

import numpy as np

import config_workflow as work


def extract_seed(cloud):
    head, tail = os.path.split(cloud)
    out = os.path.join(head, 'C2_water_seed.bin')

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {cloud}'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z} -FILTER_SF 0.5 5.'
    cmd += ' -OCTREE_NORMALS 5. -MODEL LS -ORIENT PLUS_Z -NORMALS_TO_DIP'
    cmd += f' -SET_ACTIVE_SF {work.i_dip} -FILTER_SF MIN 1.'
    cmd += ' -DENSITY 5. -TYPE KNN'
    cmd += f' -SET_ACTIVE_SF {work.i_nn} -FILTER_SF 10 MAX'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out


def propagate_1deg(compared, reference, deepness=0.2, step=None):
    # compared already contains C2C_Z, C2C and C2C_XY scalar fields
    head, tail = os.path.split(compared)
    root, ext = os.path.splitext(tail)
    if step is not None:
        out = os.path.join(head, root + f'_propagation_step_{step}.bin')
    else:
        out = os.path.join(head, root + f'_propagation.bin')
    dip = np.tan(1. * np.pi / 180)  # dip 1 degree

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {compared}'
    cmd += f' -O {reference}'
    cmd += ' -C2C_DIST -SPLIT_XY_z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_xy} -FILTER_SF 0.001 10.'  # keep closest points and avoid duplicates (i.e. xy = 0)
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z} -FILTER_SF {deepness} MAX'  # consider only points with C2 above C3
    cmd += f' -SF_OP_SF {work.i_c2c_z} DIV {work.i_c2c_xy}'  # compute the dip
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_z} -FILTER_SF {-dip} {dip}'  # filter wrt dip
    cmd += f' -O {reference} -MERGE_CLOUDS' # merge new points with the previous ones
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out
