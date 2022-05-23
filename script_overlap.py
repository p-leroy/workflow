import carteRecouvrement as overlapMap
import controle_recouvrement as overlapControl
import overlap as over

#%% THIN LINES

idir = 'C:/DATA/Brioude_30092021/05-Traitements/C3_denoised_i'
odir = r'C:\DATA\Brioude_30092021\05-Traitements\C3_denoised_i\thinned_lines'
over.thin_lines(idir, odir)

#%% OVERLAP MAP

workspace = r'C:\DATA\Brioude_30092021\05-Traitements\C3_denoised_i\thinned_lines'
params_file = "m3c2_params2.txt"
projectName = "Brioude_30092021"

param_openFile = ['standard', 'LAS', "Loire49-1"]
roots_dict = {100: [projectName + "_L", "_C3_r_denoised_i_corr_thin1_lastOnly.laz"]}
filter_dist_uncertainty = 0.5
filter_m3c2_distance = 10
line_nb_length = 3
settings = [param_openFile, roots_dict, filter_dist_uncertainty, filter_m3c2_distance, line_nb_length]

a = overlapMap.Overlap(workspace, params_file, projectName + "_C2_overlap.laz", settings)
a.preprocessing()
a.processing()

#%% OVERLAP CONTROL

workspace = r'G:\RENNES1\Loire_totale_automne2019\Loire_Sully-sur-Loire_Checy\04-QC\Recouvrement' + '//'
params_file = "m3c2_params.txt"
surface_water = "C2_ground_thin_1m_watersurface_smooth5.laz"

param_openFile = ['standard', 'LAS', "Loire45-3"]
roots_dict = {40: ["Sully-sur-Loire-Checy_M01_L", "_C3_r.laz"],
              44: ["Sully-sur-Loire-Checy_M02_L", "_C3_r.laz"],
              99: ["Sully-sur-Loire-Checy_M03_L", "_C3_r.laz"]}
filter_dist_uncertainty = 0.1

settings = [param_openFile, roots_dict, filter_dist_uncertainty, 2]

folder = "C3"

a = overlapControl.Overlap(workspace, params_file, surface_water, settings)
a.preprocessing(folder)
a.processing()

# #---Graphique---#
# list_filepath=glob.glob(workspace+folder+"/*_m3c2_*.laz")

# def func(filepath,distance_filter):
#     data=PL.lastools.readLAS_laspy(filepath,extraField=True)
#     subData1=PL.lastools.Filter_LAS(data,np.logical_not(np.isnan(data["distance_uncertainty"])))
#     del data
#     subData2=PL.lastools.Filter_LAS(subData1,subData1["distance_uncertainty"]<distance_filter)

#     m3c2_dist=subData2['m3c2_distance'][np.logical_not(np.isnan(subData2['m3c2_distance']))]
#     select=np.abs(m3c2_dist)<1
#     m3c2_dist=m3c2_dist[select]

#     if len(m3c2_dist)>100:
#         line_select=np.unique(np.random.randint(0,len(m3c2_dist),int(0.5*len(m3c2_dist))))
#         resultats=m3c2_dist[line_select]
#     else:
#         resultats=[]
#     return resultats


# #result=Parallel(n_jobs=20, verbose=2)(delayed(func)(i,filtre_dist_uncertainty) for i in list_filepath)
# #np.savez_compressed(workspace+folder+"/save_results_data_v1.npz",np.concatenate(result))


# f=np.load(workspace+folder+"/save_results_data_v1.npz")
# tab=f[f.files[0]]
# f.close()

# print(np.mean(tab))
# print(np.std(tab))

# plt.figure(1)
# plt.xlabel("Distance M3C2 (en cm)")
# plt.ylabel("Fréquence")
# plt.title('Histogramme des écarts en altitude\npour les données du canal vert')
# plt.hist(tab*100,bins=50,range=(-15,15),edgecolor='white')
# plt.ticklabel_format(axis="y",style='sci',scilimits=(0,0))
# #plt.text(x=-30,y=3000,s="Moyenne : -9cm\nEcart-type : 5.5cm")
# plt.savefig(workspace+folder+"/figure_C3_v1.png",dpi=150)
# #plt.show()
# #====================#




