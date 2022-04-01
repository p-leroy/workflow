import os

import numpy as np

try:
    import ccConfig, common_ple
    cc_cmd = ccConfig.cc_ple
    run = common_ple.exe
except ImportError:
    import plateforme_lidar.utils
    cc_cmd = plateforme_lidar.utils.QUERY_0['standard_view']
    run = plateforme_lidar.utils.Run

# INITIAL SCALAR FIELDS
# 0 [Classif] Value
# 1 Intensity
# 2 GpsTime
# 3 ReturnNumber
# 4 NumberOfReturn
# 5 ScanDirectionFlag
# 6 EdgeOfFlightLine
# 7 ScanAngleRank
# 8 PointSourceId

# OTHER SCALAR FIELDS
# 9 C2C_Z
# 10 C2C
# 11 C2C_XY
# 12 Dip (degrees)
# 13 Dip direction (degrees)
# 14 Number of neighbors (r=5)
i_c2c3_z = 9
i_c2c3 = 10
i_c2c3_xy = 11
i_dip = 12
i_nn = 14

# OTHER SCALAR FIELDS
# 12 C2C absolute distances (Z)
# 13 C2C absolute distances
# 14 C2C absolute distances (XY)
i_c2c_z = 12
i_c2c = 13
i_c2c_xy = 14


def c2c(compared, reference):
    # compute cloud to cloud distances and rename the scalar fields for further processing
    head, tail = os.path.split(compared)
    root, ext = os.path.splitext(tail)
    out = os.path.join(head, root + '_C2C.bin')

    cmd = cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {compared}'
    cmd += f' -O {reference}'
    cmd += ' -C2C_DIST -SPLIT_XY_Z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -RENAME_SF {i_c2c3_z} C2C3_Z'
    cmd += f' -RENAME_SF {i_c2c3} C2C3'
    cmd += f' -RENAME_SF {i_c2c3_xy} C2C3_XY'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    run(cmd)

    return out


def extract_seed(cloud):
    head, tail = os.path.split(cloud)
    out = os.path.join(head, 'C2_water_seed.bin')

    cmd = ccConfig.cc_ple
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {cloud}'
    cmd += f' -SET_ACTIVE_SF {i_c2c3_z} -FILTER_SF 0.5 5.'
    cmd += ' -OCTREE_NORMALS 5. -MODEL LS -ORIENT PLUS_Z -NORMALS_TO_DIP'
    cmd += f' -SET_ACTIVE_SF {i_dip} -FILTER_SF MIN 1.'
    cmd += ' -DENSITY 5. -TYPE KNN'
    cmd += f' -SET_ACTIVE_SF {i_nn} -FILTER_SF 10 MAX'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    run(cmd)

    return out


def propagate_1deg(compared, reference, step=None):
    # compared already contains C2C_Z, C2C and C2C_XY scalar fields
    head, tail = os.path.split(compared)
    root, ext = os.path.splitext(tail)
    if step is not None:
        out = os.path.join(head, root + f'_propagation_step_{step}.bin')
    else:
        out = os.path.join(head, root + f'_propagation.bin')
    dip = np.tan(1. * np.pi / 180)  # dip 1 degree

    cmd = cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {compared}'
    cmd += f' -O {reference}'
    cmd += ' -C2C_DIST -SPLIT_XY_z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {i_c2c_xy} -FILTER_SF 0.001 10.'  # keep closest points and avoid duplicates (i.e. xy = 0)
    cmd += f' -SET_ACTIVE_SF {i_c2c3_z} -FILTER_SF 0.2 MAX'  # consider only points with C2 above C3
    cmd += f' -SF_OP_SF {i_c2c_z} DIV {i_c2c_xy}'  # compute the dip
    cmd += f' -SET_ACTIVE_SF {i_c2c_z} -FILTER_SF {-dip} {dip}'  # filter wrt dip
    cmd += f' -O {reference} -MERGE_CLOUDS' # merge new points with the previous ones
    cmd += f' -SAVE_CLOUDS FILE {out}'
    run(cmd)

    return out
