import glob
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig()

global_shift_vieux_rhin = (-1037000.0, -6741000.0, 0.0)
global_shift_vieux_rhin_fwf = (-1040000., -6770000., 0.)

try:
    import ccConfig
    import common_ple
    cc_cmd = ccConfig.cc_ple

    def custom_run(cmd):
        return common_ple.exe(cmd, debug=True)

    run = custom_run
    logger.info("[ple imports]")
except ImportError:
    import plateforme_lidar.utils
    cc_cmd = plateforme_lidar.utils.QUERY_0['standard_view']
    run = plateforme_lidar.utils.Run
    logger.info("[not ple imports]")

# INITIAL SCALAR FIELDS
# 0 [Classif] Value (added by lastools)
# 1 Intensity
# 2 GpsTime
# 3 ReturnNumber
# 4 NumberOfReturn
# 5 ScanDirectionFlag
# 6 EdgeOfFlightLine
# 7 ScanAngleRank
# 8 PointSourceId

i_point_source_id = 8

# 9 C2C3_XY
# 10 C2C3
# 11 C2C3_X
# 12 C2C3_Y
# 13 C2C3_Z
i_c2c3_xy = 9
i_c2c3 = 10
i_c2c3_x = 11  # REMOVED
i_c2c3_y = 12  # REMOVED
i_c2c3_z = 11  # AFTER REMOVAL OF X AND Y

# 14 Dip (degrees)
# 15 Dip direction (degrees)
# 16 Number of neighbors (r=5)
i_dip = 12
i_nn = 14

# 12 C2C absolute distances (XY)
# 13 C2C absolute distances
# 14 C2C absolute distances (X)
# 15 C2C absolute distances (Y)
# 16 C2C absolute distances (Z)

i_c2c_xy = 12
i_c2c = 13
i_c2c_x = 14  # REMOVED
i_c2c_y = 15  # REMOVED
i_c2c_z = 14  # AFTER REMOVAL OF X AND Y



def exists(path):
    if not os.path.exists(path):
        print(f'file does not exists! {path}')
        return False
    else:
        return True


def head_tail_root_ext(path):
    head, tail = os.path.split(path)
    root, ext = os.path.splitext(tail)
    return head, tail, root, ext


def remove(files):
    for file in glob.glob(files):
        os.remove(file)


def get_shift(config):
    # the shift comes from
    # 1) the intensity correction, i.e. imax_minus_i and intensity_class SF have been added
    # 2) the classification field added by lastools
    if config == 'classified':
        shift = 0
    elif config == 'i_corr_classified':
        shift = 2
    elif config == 'i_corr_not_classified':
        shift = 1
    elif config == 'not_classified':
        shift = -1
    else:
        print(f'[get_shift] config unknown: {config}')
        shift = None
    return shift


def c2c_c2c3(compared, reference, config, global_shift):
    # compute cloud to cloud distances and rename the scalar fields for further processing
    head, tail = os.path.split(compared)
    root, ext = os.path.splitext(tail)
    out = os.path.join(head, root + '_C2C3.bin')

    shift = get_shift(config)

    cmd = cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT BIN -AUTO_SAVE OFF'
    if global_shift == 'auto':
        cmd += f' -O -GLOBAL_SHIFT AUTO {compared}'
    else:
        shift_x = global_shift[0]
        shift_y = global_shift[1]
        shift_z = global_shift[2]
        cmd += f' -O -GLOBAL_SHIFT {shift_x} {shift_y} {shift_z} {compared}'
    cmd += f' -O {reference}'
    cmd += ' -C2C_DIST -SPLIT_XY_Z'
    cmd += ' -POP_CLOUDS'
    cmd += f' -REMOVE_SF {i_c2c3_y + shift}'
    cmd += f' -REMOVE_SF {i_c2c3_x + shift}'
    cmd += f' -RENAME_SF {i_c2c3_z + shift} C2C3_Z'
    cmd += f' -RENAME_SF {i_c2c3 + shift} C2C3'
    cmd += f' -RENAME_SF {i_c2c3_xy + shift} C2C3_XY'
    cmd += f' -SAVE_CLOUDS FILE {out}'
    run(cmd)

    return out
