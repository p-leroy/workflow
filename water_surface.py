import os

import numpy as np

import config_workflow as work


def extract_seed(cloud):
    if not work.exists(cloud):
        return
    head, tail = os.path.split(cloud)
    odir = os.path.join(head, 'water_surface')
    if not os.path.exists(odir):
        os.makedirs(odir)
    out = os.path.join(odir, 'C2_water_seed.bin')

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


def propagate_1deg(c2_cloud_with_c2c3_dist, current_surface, deepness=0.2, step=None):
    # c2_cloud_with_c2c3_dist shall contain C2C3_Z, C2C3 and C2C3_XY scalar fields
    if not work.exists(c2_cloud_with_c2c3_dist):
        return
    if not work.exists(current_surface):
        return
    head, tail, root, ext = work.head_tail_root_ext(c2_cloud_with_c2c3_dist)
    odir = os.path.join(head, 'water_surface')

    if step is not None:
        out = os.path.join(odir, root + f'_propagation_step_{step}.bin')
    else:
        out = os.path.join(odir, root + f'_propagation.bin')
    dip = np.tan(1. * np.pi / 180)  # dip 1 degree

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {c2_cloud_with_c2c3_dist}'
    cmd += f' -O {current_surface}'
    cmd += ' -C2C_DIST -SPLIT_XY_z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_xy} -FILTER_SF 0.001 10.'  # keep closest points and avoid duplicates (i.e. xy = 0)
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z} -FILTER_SF {deepness} MAX'  # consider only points with C2 above C3
    cmd += f' -SF_OP_SF {work.i_c2c_z} DIV {work.i_c2c_xy}'  # compute the dip
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_z} -FILTER_SF {-dip} {dip}'  # filter wrt dip
    cmd += f' -O {current_surface} -MERGE_CLOUDS' # merge new points with the previous ones
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out
