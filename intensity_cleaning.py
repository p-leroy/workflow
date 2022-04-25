import os

import matplotlib.pyplot as plt
import numpy as np

import cc
import config_workflow as work


i_intensity = 0
i_intensity_in_raster = 1  # after the Height grid values field
i_imax_minus_i = 8


def add_sf_imax_minus_i(line):
    print('[add_sf_imax_minus_i]')
    if not work.exists(line):
        return

    head, tail, root, ext = work.head_tail_root_ext(line)
    odir = os.path.join(head, 'lines_i_correction')
    if not os.path.exists(odir):
        os.makedirs(odir)
    pc_with_imax_minus_i = os.path.join(odir, root + '_i.sbf')
    raster = os.path.join(odir, root + '_raster.sbf')

    cmd = work.cc_cmd
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT SBF -AUTO_SAVE OFF'
    cmd += f' -O {line}'  # open the line
    cmd += f' -SET_ACTIVE_SF {i_intensity} -FILTER_SF MIN 400.'  # filter by intensity values
    cmd += ' -RASTERIZE -GRID_STEP 1 -VERT_DIR 2 -PROJ AVG -SF_PROJ MAX -OUTPUT_CLOUD'  # compute raster
    # rename the scalar field Intensity to a more convenient name for its later use: imax_minus_i
    # note: the raster is the only open entity at this time of the process
    cmd += f' -RENAME_SF {i_intensity_in_raster} imax_minus_i'
    cmd += f' -O {line}'  # re-open the line as it has been replaced in memory during -RASTERIZE -OUTPUT_CLOUD
    cmd += f' -SF_INTERP {i_intensity_in_raster}'  # interpolate scalar field from the raster to the original cloud
    cmd += f' -SF_OP_SF LAST SUB {i_intensity}'  # compute (imax - intensity), done in place
    cmd += f' -SAVE_CLOUDS FILE "{raster} {pc_with_imax_minus_i}"'

    work.run(cmd)

    print(f'remove {raster}')
    os.remove(raster)
    os.remove(raster + '.data')

    return pc_with_imax_minus_i


def qc_check(pc_with_imax_minus_i, threshold=83, shift=103):
    print('[qc_check]')
    print(f'open {pc_with_imax_minus_i}')
    head, tail = os.path.split(pc_with_imax_minus_i)
    root, ext = os.path.splitext(tail)
    odir = os.path.join(head, 'qc')
    if not os.path.exists(odir):
        os.makedirs(odir)

    pc, sf, config = cc.read_sbf(pc_with_imax_minus_i)  # read the SBF file

    # limit intensity values range
    loc = sf[:, i_intensity] < 400
    sf = sf[loc, :]
    imax_minus_i = sf[:, i_imax_minus_i]
    intensity = sf[:, i_intensity]

    # low and high histograms
    print('compute and save histogram of corrected intensities')
    low = intensity[(threshold < imax_minus_i) & (imax_minus_i < 200)]
    high = intensity[(0 < imax_minus_i) & (imax_minus_i < threshold)]  - shift
    hist_low = np.histogram(low, bins=256)
    hist_high = np.histogram(high, bins=256)
    plt.plot(hist_low[1][:-1], hist_low[0], '.b', label='low intensities (not shifted)')
    plt.plot(hist_high[1][:-1], hist_high[0], '.r', label=f'high intensities shifted by {shift}')
    name = os.path.join(odir, root + '_histo_intensity_corrected')
    plt.xlabel('intensity bins')
    plt.ylabel('N')
    plt.xlim(0, 400)
    plt.title(tail)
    plt.legend()
    plt.grid()
    plt.savefig(name)
    plt.close()
    print(f'   => {name}')

    # intensity histogram
    print(f'compute and save histogram of original intensity')
    histogram = np.histogram(intensity, bins=256)
    i_corr = np.r_[low, high]
    histogram_corr = np.histogram(i_corr, bins=256)
    plt.plot(histogram_corr[1][:-1], histogram_corr[0] / 2, 'o', label='corrected intensity (N/2')
    plt.plot(histogram_corr[1][:-1], histogram_corr[0], '.-', label='corrected intensity')
    plt.plot(histogram[1][:-1], histogram[0], '.-', label='initial intensity')
    name = os.path.join(odir, root + '_histo_intensity')
    plt.xlabel('intensity bins')
    plt.ylabel('N')
    plt.xlim(0, 400)
    plt.title(tail)
    plt.legend()
    plt.grid()
    plt.savefig(name)
    plt.close()
    print(f'   => {name}')

def correct_intensities_and_add_class(pc_with_imax_minus_i, threshold=83, shift=103):
    print('[correct_intensities_and_add_class]')
    if not os.path.exists(pc_with_imax_minus_i):
        print(f'file does not exists! {pc_with_imax_minus_i}')
        return

    head, tail = os.path.split(pc_with_imax_minus_i)
    root, ext = os.path.splitext(tail)
    high = os.path.join(head, root + '_high.sbf')
    low = os.path.join(head, root + '_low.sbf')
    merged = os.path.join(head, root + '_corr.sbf')

    cmd = work.cc_cmd
    # high intensities
    cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT SBF -AUTO_SAVE OFF'
    cmd += f' -O -GLOBAL_SHIFT FIRST {pc_with_imax_minus_i}'
    cmd += f' -SET_ACTIVE_SF LAST -FILTER_SF -10 {threshold}'  # filter (Imax - intensity)
    cmd += f' -SF_OP {i_intensity} SUB {shift}'  # shift intensity values, done in place
    cmd += ' -SF_ADD_CONST intensity_class 1'
    cmd += f' -SAVE_CLOUDS FILE {high}'
    cmd += ' -CLEAR_CLOUDS'
    # low intensities
    cmd += f' -O -GLOBAL_SHIFT FIRST {pc_with_imax_minus_i}'
    cmd += f' -SET_ACTIVE_SF LAST -FILTER_SF {threshold} 400'  # filter (Imax - intensity)
    cmd += ' -SF_ADD_CONST intensity_class 0'
    cmd += f' -SAVE_CLOUDS FILE {low}'
    # merge the clouds
    cmd += f' -O {high} -MERGE_CLOUDS -SAVE_CLOUDS FILE {merged}'
    work.run(cmd)

    # remove temporary files
    print(f'remove {high}')
    os.remove(high)
    os.remove(high + '.data')
    print(f'remove {low}')
    os.remove(low)
    os.remove(low + '.data')
    print(f'remove {pc_with_imax_minus_i}')
    os.remove(pc_with_imax_minus_i)
    os.remove(pc_with_imax_minus_i + '.data')

    return merged
