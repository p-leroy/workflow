# coding: utf-8
# Baptiste Feldmann
import plateforme_lidar as PL
import numpy as np
import glob, os, time, shutil
from joblib import Parallel, delayed

def corbathy_discret(filepath, data_sbet):
    offset_name = -10
    output_suffix = "_corbathy"

    # open batyhmetry file
    in_data = PL.lastools.readLAS(filepath, extraField=True)

    select = in_data.depth < 0.01
    data_under_water = PL.lastools.Filter_LAS(in_data, select)
    data_above_water = PL.lastools.Filter_LAS(in_data, np.logical_not(select))
    del in_data
    
    gps_time = data_under_water.gps_time
    depth_app = data_under_water.depth
    
    # compute new positions
    data_interp = PL.sbet.interpolate(data_sbet[0], data_sbet[1], gps_time)
    coords_true, depth_true = PL.calculs.correction3D(data_under_water.XYZ, depth_app, data_interp[:, 0:3])
    
    # write results in las files
    depth_all = np.concatenate((np.round(depth_true, decimals=2), np.array([None] * len(data_above_water))))
    extra = [(("depth", "float32"), depth_all)]
    data_under_water.XYZ = coords_true
    data_corbathy = PL.lastools.Merge_LAS([data_under_water, data_above_water])
    PL.lastools.writeLAS(filepath[0:offset_name] + output_suffix+".laz", data_corbathy, format_id=1, extraField=extra)

def corbathy_fwf(filepath):
    offset_name = -10
    output_suffix = "_corbathy"
    # open bathymetry file
    in_data = PL.lastools.readLAS_laspy(filepath,True)

    vect_app = np.vstack([in_data.x_t,in_data.y_t,in_data.z_t]).transpose()
    vect_true_all = PL.calculs.correction_vect(vect_app)
    in_data.x_t, in_data.y_t, in_data.z_t = vect_true_all[:,0], vect_true_all[:,1], vect_true_all[:,2]
    
    select = in_data.depth<0.01
    data_under_water = PL.lastools.Filter_LAS(in_data,select)
    data_above_water = PL.lastools.Filter_LAS(in_data, np.logical_not(select))
    vect_app_under_water = vect_app[select]
    del in_data

    depth_app = data_under_water.depth
    # compute new positions
    coords_true, depth_true = PL.calculs.correction3D(data_under_water.XYZ, depth_app, vectorApp=vect_app_under_water)
    
    # write results in las files
    depth_all = np.concatenate((np.round(depth_true,decimals=2), np.array([None]*len(data_above_water))))
    extra=[(("depth", "float32"), depth_all)]

    data_under_water.XYZ = coords_true
    data_corbathy = PL.lastools.Merge_LAS([data_under_water,data_above_water])

    #return data_corbathy, extra, metadata['vlrs']
    #PL.lastools.writeLAS(filepath[0:offsetName] + "_corbathy2.laz", dataCorbathy, format_id=4, extraField=extra)
    PL.lastools.writeLAS(filepath[0:offset_name] + output_suffix + ".laz", data_corbathy, format_id=9)
    shutil.copyfile(filepath[0:-4] + ".wdp", filepath[0:offset_name] + output_suffix + ".wdp")


if __name__ != '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Correction bathy command...')
    parser.add_argument('-i', type=str)
    parser.add_argument('-sbet', type=str)
    parser.add_argument('-fwf', action='store_true')
    parser.add_argument('-n_jobs', type=int,default=1)
    args = parser.parse_args()
    chemin = args.i
    file_sbet = args.sbet
    opt_fwf = args.fwf
    cores = args.n_jobs
else:
    chemin = 'C:/DATA/Brioude_30092021/05-Traitements/C3_raw_bathy.laz'
    file_sbet = "params_sbet_Brioude.txt"
    opt_fwf = False
    cores = 1

workspace, tail = os.path.split(chemin)

list_path = glob.glob(chemin)
print("[Bathymetric correction] : " + str(len(list_path)) + " files found !")
debut = time.time()

if opt_fwf:
    print("[Bathymetric correction] : FWF mode Waiting...")
    if len(list_path) == 1:
        corbathy_fwf(chemin)
    else:
        Parallel(n_jobs=cores, verbose=1)(delayed(corbathy_fwf)(f) for f in list_path)
else:
    print("[Bathymetric correction] : SBET data processes, waiting...")
    sbet_config = PL.sbet.Sbet_config(os.path.join(workspace, file_sbet))
    print("[Bathymetric correction] : SBET data processes, done !")
    print("[Bathymetric correction] : Discrete mode Waiting...")
    if len(list_path) == 1:
        corbathy_discret(chemin, sbet_config)
    else:
        Parallel(n_jobs=cores, verbose=1)(
            delayed(corbathy_discret)(f, sbet_config) for f in list_path)

fin = time.time()
print("[Bathymetric correction] : Complete in " + str(round(fin - debut, 1)) + " sec")
