import os

import config_workflow as work


i_intensity = 0
i_intensity_in_raster = 1  # after the Height grid values field


def intensity_mitigation(line):
    head, tail = os.path.split(line)
    root, ext = os.path.splitext(tail)
    out = os.path.join(head, 'intensity_corrected_lines', root + '_corr.sbf')
    raster = os.path.join(head, 'intensity_corrected_lines', root + '_raster.sbf')

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT SBF -AUTO_SAVE OFF'
    cmd += f' -O {line}'  # open the line
    cmd += f' -SET_ACTIVE_SF {i_intensity} -FILTER_SF MIN 400.'  # filter by intensity values
    cmd += ' -RASTERIZE -GRID_STEP 1 -VERT_DIR 2 -PROJ AVG -SF_PROJ MAX -OUTPUT_CLOUD'  # compute raster
    cmd += f' -RENAME_SF {i_intensity_in_raster} Imax'  # rename intensity in the raster to Imax
    cmd += f' -O {line}'  # re-open the line as it has been replaced by RASTERIZE + OUTPUT_CLOUD
    cmd += f' -SF_INTERP {i_intensity_in_raster}'  # interpolate scalar field from the raster to the original cloud
    cmd += f' -SF_OP_SF LAST SUB {i_intensity}'  # compute Imax - intensity, done in place
    # split into two clouds
    # shift one cloud
    # merge the clouds
    cmd += f' -SAVE_CLOUDS FILE "{raster} {out}"'
    work.run(cmd)

    return out
