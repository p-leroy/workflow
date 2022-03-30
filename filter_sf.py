import os
import subprocess

import ccConfig
import common_ple as ple

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
i_c2c_z = 9
i_c2c = 10
i_c2c_xy = 11
i_dip = 12
i_nn = 14

# OTHER SCALAR FIELDS
# 12 C2C absolute distances (Z)
# 13 C2C absolute distances
# 14 C2C absolute distances (XY)
i_c2c_ad_z = 12
i_c2c_ad = 13
i_c2c_ad_xy = 14


def extract_water_surface_seed(cloud):
    head, tail = os.path.split(cloud)
    out = os.path.join(head, 'C2_water_seed.bin')

    cmd = ccConfig.cc_ple
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {cloud}'
    cmd += f' -SET_ACTIVE_SF {i_c2c_z} -FILTER_SF 0.5 5.'
    cmd += ' -OCTREE_NORMALS 5. -MODEL LS -ORIENT PLUS_Z -NORMALS_TO_DIP'
    cmd += f' -SET_ACTIVE_SF {i_dip} -FILTER_SF MIN 1.'
    cmd += ' -DENSITY 5. -TYPE KNN'
    cmd += f' -SET_ACTIVE_SF {i_nn} -FILTER_SF 10 MAX'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    ple.exe(cmd, debug=True)

    return out


def c2c(compared, reference):
    head, tail = os.path.split(compared)
    root, ext = os.path.splitext(tail)
    out = os.path.join(head, root + '_C2C.bin')

    cmd = ccConfig.cc_ple
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {compared}'
    cmd += f' -O {reference}'
    cmd += ' -C2C_DIST -MERGE_XY'
    cmd += ' -POP_CLOUDS'
    cmd += f' -RENAME_SF {i_c2c_z} C2C_Z'
    cmd += f' -RENAME_SF {i_c2c} C2C'
    cmd += f' -RENAME_SF {i_c2c_xy} C2C_XY'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    ple.exe(cmd, debug=True)

    return out


def propagate_water_surface(compared, reference, step=None):
    # compared already contains C2C_Z, C2C and C2C_XY scalar fields
    head, tail = os.path.split(compared)
    root, ext = os.path.splitext(tail)
    if step is not None:
        out = os.path.join(head, root + f'_propagation_step_{step}.bin')
    else:
        out = os.path.join(head, root + f'_propagation.bin')

    cmd = ccConfig.cc_ple
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {compared}'
    cmd += f' -O {reference}'
    cmd += ' -C2C_DIST -MERGE_XY'
    cmd += ' -POP_CLOUDS'
    cmd += f' -SET_ACTIVE_SF {i_c2c_ad_xy} -FILTER_SF MIN 5.'
    cmd += f' -SET_ACTIVE_SF {i_c2c_ad_z} -FILTER_SF -0.1 0.1'
    cmd += f' -SET_ACTIVE_SF {i_c2c_z} -FILTER_SF 0.2 MAX'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    ple.exe(cmd, debug=True)

    return out


def propagate_water_surface_with_C3(compared, reference, step=None):
    # compared already contains C2C_Z, C2C and C2C_XY scalar fields
    head, tail = os.path.split(compared)
    root, ext = os.path.splitext(tail)
    if step is not None:
        out = os.path.join(head, root + f'_propagation_step_{step}.bin')
    else:
        out = os.path.join(head, root + f'_propagation.bin')

    cmd = ccConfig.cc_ple
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    cmd += f' -O {compared}'
    cmd += f' -O {reference}'
    cmd += ' -C2C_DIST -MERGE_XY'
    cmd += ' -POP_CLOUDS'
    # select points in C3 which are close to the water surface in the xy plane
    cmd += f' -SET_ACTIVE_SF {i_c2c_ad_xy} -FILTER_SF MIN 5.'
    # select points which are below the surface
    cmd += f' -SET_ACTIVE_SF {i_c2c_z} -FILTER_SF MIN -0.2 '
    cmd += f' -SAVE_CLOUDS FILE {out}'
    ple.exe(cmd, debug=True)

    return out


idir = r'C:\DATA\Brioude_30092021\05-Traitements'
c2_thin = os.path.join(idir, 'C2_ground_thin_1m.laz')
c3_thin = os.path.join(idir, 'C3_ground_thin_1m.laz')

c2_c2c = c2c(c2_thin, c3_thin)
c3_c2c = c2c(c3_thin, c2_thin)
water_surface_seed = extract_water_surface_seed(c2_c2c)
water_surface = propagate_water_surface(c2_c2c, water_surface_seed)
water_surface = propagate_water_surface(c2_c2c, water_surface)

step = 0
water_surface = propagate_water_surface(c2_c2c, water_surface_seed, step=step)
for step in range(step+1, step + 20):
    water_surface = propagate_water_surface(c2_c2c, water_surface, step=step)
