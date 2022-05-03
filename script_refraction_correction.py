import refraction_correction as corr

# define parameters
input = 'C:/DATA/Brioude_30092021/05-Traitements/C3_raw_bathy.laz'
sbet = "params_sbet_Brioude.txt"
fwf = False
n_jobs= 1

corr.do_work(input, sbet, n_jobs, fwf)
