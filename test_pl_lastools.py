import os

import plateforme_lidar as pl

line11 = r'C:\DATA\Brioude_30092021\05-Traitements\C3\denoised\Brioude_30092021_L11_C3_r_1.laz'
line11_alt = r'C:\DATA\Brioude_30092021\05-Traitements\C3\denoised\lines_i_correction\Brioude_30092021_L11_C3_r_1.las'
line11_sbf = r'C:\DATA\Brioude_30092021\05-Traitements\C3\denoised\lines_i_correction\Brioude_30092021_L11_C3_r_1.sbf'

out = pl.lastools.ReadLAS(line11)
out_alt = pl.lastools.ReadLAS(line11_alt)

translation = {'Intensity' : 'intensity',
               'GpsTime' : None,
               'ReturnNumber' : 'return_number',
               'NumberOfReturns' : 'number_of_returns',
               'ScanDirectionFlag' : 'scan_direction_flag',
               'EdgeOfFlightLine' : 'edge_of_flight_line',
               'ScanAngleRank': None,
               'PointSourceId': None}

