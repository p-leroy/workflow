import os

import numpy as np

import config_workflow as work


def extract_seed(cloud, config):
    if not work.exists(cloud):
        return
    head, tail = os.path.split(cloud)
    head, tail, root, ext = work.head_tail_root_ext(cloud)
    odir = os.path.join(head, 'water_surface')
    os.makedirs(odir, exist_ok=True)
    out = os.path.join(odir, root + f'_water_surface_seed.bin')

    shift = work.get_shift(config)

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O -GLOBAL_SHIFT AUTO {cloud}'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z + shift} -FILTER_SF 0.5 5.'
    cmd += ' -OCTREE_NORMALS 5. -MODEL LS -ORIENT PLUS_Z -NORMALS_TO_DIP'
    cmd += f' -SET_ACTIVE_SF {work.i_dip + shift} -FILTER_SF MIN 1.'
    cmd += ' -DENSITY 5. -TYPE KNN'
    cmd += f' -SET_ACTIVE_SF LAST -FILTER_SF 10 MAX'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out


def propagate_1deg(c2_cloud_with_c2c3_dist, current_surface, config, deepness=0.2, step=None):
    # c2_cloud_with_c2c3_dist shall contain C2C3_Z, C2C3 and C2C3_XY scalar fields
    if not work.exists(c2_cloud_with_c2c3_dist):
        return
    if not work.exists(current_surface):
        return
    head, tail, root, ext = work.head_tail_root_ext(c2_cloud_with_c2c3_dist)
    odir = os.path.join(head, 'water_surface')

    if step is not None:
        out = os.path.join(odir, root + f'_propagation_{step}.bin')
    else:
        out = os.path.join(odir, root + f'_propagation.bin')
    dip = np.tan(1. * np.pi / 180)  # dip 1 degree

    shift = work.get_shift(config)

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O -GLOBAL_SHIFT AUTO {c2_cloud_with_c2c3_dist}'
    cmd += f' -O -GLOBAL_SHIFT FIRST {current_surface}'
    cmd += ' -C2C_DIST -SPLIT_XY_z'
    cmd += f' -REMOVE_SF {work.i_c2c_y + shift}'
    cmd += f' -REMOVE_SF {work.i_c2c_x + shift}'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_xy + shift} -FILTER_SF 0.001 10.'  # keep closest points and avoid duplicates (i.e. xy = 0)
    cmd += f' -SET_ACTIVE_SF {work.i_c2c3_z + shift} -FILTER_SF {deepness} MAX'  # consider only points with C2 above C3
    cmd += f' -SF_OP_SF {work.i_c2c_z + shift} DIV {work.i_c2c_xy + shift}'  # compute the dip
    cmd += f' -SET_ACTIVE_SF {work.i_c2c_z + shift} -FILTER_SF {-dip} {dip}'  # filter wrt dip
    cmd += f' -O -GLOBAL_SHIFT FIRST {current_surface} -MERGE_CLOUDS' # merge new points with the previous ones
    cmd += f' -SAVE_CLOUDS FILE {out}'
    work.run(cmd)

    return out
