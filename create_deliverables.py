# coding: utf-8
# Baptiste Feldmann

import glob, os, shutil
from joblib import delayed, Parallel

import plateforme_lidar as PL


def clean(path):
    laz = os.path.join(path, "*.laz")
    lax = os.path.join(path, "*.lax")
    [os.remove(i) for i in glob.glob(laz)]
    [os.remove(i) for i in glob.glob(lax)]

    tiles_d = os.path.join(path, "dalles")
    list_dir = os.listdir(tiles_d)
    [shutil.move(os.path.join(tiles_d, i), os.path.join(path, i)) for i in list_dir]
    shutil.rmtree(tiles_d)


class Deliverable(object):
    def __init__(self, workspace, resolution, root_name):
        self.raster_path = None
        self.raster_dir = None
        self.workspace = workspace
        self.root_name = root_name
        self.pixel_size = resolution
        if self.pixel_size < 1:
            self.pixel_size_name = str(int(self.pixel_size * 100)) + "cm"
        else:
            self.pixel_size_name = str(int(self.pixel_size)) + "m"
        self.channel_settings = {"C2" : ["C2"], "C3" : ["C3"], "C2C3" : ["C2", "C3"]}
        self.mkp_settings = {"ground" : ["bathy", "ground"], "nonground" : ["vegetation", "building"]}

    def DTM(self, channel):
        self.raster_dir = "_".join(["MNT", channel, self.pixel_size_name])
        self.raster_path = os.path.join(self.workspace, self.raster_dir)

        odir = self.raster_path
        os.mkdir(odir)
        if "C2" in channel:
            i = os.path.join(self.workspace, "LAS", "C2", "*.laz")
            PL.utils.Run(f"las2las -i {i} -keep_class 2 -cores 50 -odir {odir} -olaz")
        if "C3" in channel:
            i = os.path.join(self.workspace, "LAS", "C3", "*.laz")
            PL.utils.Run(f"las2las -i {i} -keep_class 2 10 16 -cores 50 -odir {odir} -olaz")

        out_name = [self.root_name, "MNT", self.pixel_size_name + ".tif"]
        odir = os.path.join(self.raster_path, "dalles")
        os.mkdir(odir)
        i_laz = os.path.join(self.raster_path, "*.laz")
        i_dalles = os.path.join(odir, "*.laz")
        o = os.path.join(self.raster_path, "dalles", self.root_name + "_MNT.laz")
        PL.utils.Run(f"lasindex -i {i_laz} -cores 50")
        PL.utils.Run(f"lastile -i {i_laz} -tile_size 1000 -buffer 250 -cores 45 -odir {odir} -o {o}")
        PL.utils.Run(f"blast2dem -i {i_dalles} -step {self.pixel_size} -kill 250 -use_tile_bb -epsg 2154 -cores 50 -otif")

        i_tif = glob.glob(os.path.join(self.raster_path, "dalles", "*.tif"))
        o_merge = os.path.join(self.raster_path, "dalles", "_".join(out_name))
        PL.gdal.Merge(i_tif, o_merge)
        clean(self.raster_path)

    def DSM(self, channel, opt="vegetation"):
        '''
        opt for MNS : "vegetation" or "vegetation_building"
        '''
        self.raster_dir = "_".join(["MNS", opt, channel, self.pixel_size_name])
        self.raster_path = os.path.join(self.workspace, self.raster_dir)

        os.mkdir(self.workspace + self.raster_dir)
        out_name=[self.root_name, "MNS", self.pixel_size_name + ".tif"]

        if "C2" in channel:
            if opt=="vegetation":
                PL.utils.Run("las2las -i " + self.workspace + "LAS/C2/*.laz -keep_class 2 5 -cores 50 -odir " + self.workspace + self.raster_dir + " -olaz")
            else:
                PL.utils.Run("las2las -i " + self.workspace + "LAS/C2/*.laz -keep_class 2 5 6 -cores 50 -odir " + self.workspace + self.raster_dir + " -olaz")
        if "C3" in channel:
            if opt=="vegetation":
                PL.utils.Run("las2las -i " + self.workspace + "LAS/C3/*.laz -keep_class 2 5 10 16 -cores 50 -odir " + self.workspace + self.raster_dir + " -olaz")
            else:
                PL.utils.Run("las2las -i " + self.workspace + "LAS/C3/*.laz -keep_class 2 5 6 10 16 -cores 50 -odir " + self.workspace + self.raster_dir + " -olaz")

        os.mkdir(self.workspace + self.raster_dir + "/dalles")
        os.mkdir(self.workspace + self.raster_dir + "/dalles/thin")

        PL.utils.Run("lasindex -i " + self.workspace + self.raster_dir + "/*.laz -cores 50")
        PL.utils.Run("lastile -i " + self.workspace + self.raster_dir + "/*.laz -tile_size 1000 -buffer 250 -cores 45 -odir " + self.workspace + self.raster_dir + "/dalles -o " + self.workspace + self.raster_dir + "/dalles/" + self.root_name + "_MNS.laz")
        PL.utils.Run("lasthin -i " + self.workspace + self.raster_dir + "/dalles/*.laz -step 0.2 -highest -cores 50 -odir " + self.workspace + self.raster_dir + "/dalles/thin -olaz")
        PL.utils.Run("blast2dem -i " + self.workspace + self.raster_dir + "/dalles/thin/*.laz -step " + str(self.pixel_size) + " -kill 250 -use_tile_bb -epsg 2154 -cores 50 -otif")
        PL.gdal.Merge(glob.glob(self.workspace + self.raster_dir + "/dalles/thin/*.tif"), self.workspace + self.raster_dir + "/dalles/thin/" + "_".join(out_name))

        clean(self.raster_path)

    def DCM(self,channel):
        self.raster_dir= "_".join(["MNC", channel, self.pixel_size_name])
        self.raster_path = os.path.join(self.workspace, self.raster_dir)

        os.mkdir(self.workspace + self.raster_dir)
        MNCpath= self.workspace + self.raster_dir + "/"
        MNSpath= self.workspace +"MNS_vegetation_" + channel +"_" + self.pixel_size_name + "/thin/"
        MNTpath= self.workspace +"MNT_" + channel + "_" + self.pixel_size_name + "/"
        if not (os.path.exists(MNSpath + self.root_name + "_MNS_" + self.pixel_size_name + ".tif") and os.path.exists(MNTpath + self.root_name + "_MNT_" + self.pixel_size_name + ".tif")):
            raise OSError("MNS_vegetation or MNT aren't already computed !")

        outName = [self.root_name, "MNC", self.pixel_size_name + ".tif"]
        listMNS = [os.path.split(i)[1] for i in glob.glob(MNSpath + "*00.tif")]
        listMNT = []
        listMNC = []
        for i in listMNS:
            splitCoords = i.split(sep="_")[-2::]
            listMNT += [self.root_name + "_MNT_" + "_".join(splitCoords)]
            listMNC += [self.root_name + "_MNC_" + "_".join(splitCoords)]
        Parallel(n_jobs=50, verbose=2)(delayed(PL.gdal.RasterCalc)("A-B", MNCpath + listMNC[i], MNSpath + listMNS[i], MNTpath + listMNT[i]) for i in range(0,len(listMNS)))
        PL.gdal.Merge(glob.glob(MNCpath + "*.tif"), MNCpath + "_".join(outName))

    def Density(self,channel):
        #not finish
        DTM_path= self.workspace +"_".join(["MNT", channel, self.pixel_size_name]) + "/"
        if not os.path.exists(DTM_path + self.root_name + "_MNT_" + self.pixel_size_name + ".tif"):
            raise OSError("MNT isn't already computed !")

        outName=[self.root_name, "MNT", "density", self.pixel_size_name + ".tif"]
        os.mkdir(DTM_path+"density")
        os.mkdir(DTM_path+"density/final")

        PL.utils.Run("lasgrid -i "
                     + DTM_path
                     + "*.laz -step "
                     + str(self.pixel_size)
                     + " -use_tile_bb -counter_16bit -drop_class 10 -cores 50 -epsg 2154 -odir "
                     + DTM_path
                     + "density -odix _density -otif")
        listMNT=[os.path.split(i)[1] for i in glob.glob(DTM_path + "*00.tif")]
        Parallel(n_jobs=50, verbose=2)(delayed(PL.gdal.HoleFilling)(DTM_path+"density/" + i[0:-4]+"_density.tif", DTM_path+i) for i in listMNT)
        PL.gdal.Merge(glob.glob(DTM_path + "density/final/*.tif"),DTM_path+"density/final/" + "_".join(outName))

        [os.remove(i) for i in glob.glob(DTM_path + "density/*_density.tif")]
        listDir=os.listdir(DTM_path + "density/final")
        [shutil.move(DTM_path + "density/final/" + i,DTM_path + "density/" + i) for i in listDir]
        shutil.rmtree(DTM_path + "density/final")

    def MKP(self,channel,mode,settings=[]):
        '''
        mode : ground or nonground
        settings : ground=[vertical,horiz], nonground=[thinning step]
        '''
        #not finish
        self.raster_dir= "MKP_" + mode
        outName = [self.root_name, "MKP", channel, mode + ".laz"]
        os.mkdir(self.workspace + self.raster_dir)
        os.mkdir(self.workspace + self.raster_dir + "/dalles")

        if mode == "ground":
            listFolder = ["C3_bathy"] + [i + "ground" for i in self.channel_settings[channel]]
            thinning = "-step 5 -adaptive " + str(settings[0]) + " " + str(settings[1])
        elif mode == "nonground":
            listFolder = []
            for i in ["vegetation","building"]:
                listFolder += [c + i for c in self.channel_settings[channel]]
            thinning="-step "+str(settings[0]) + "-random"
        else:
            raise OSError("MKP works for only ground or nonground modes")

        for folder in listFolder:
             Parallel(n_jobs=50, verbose=1)(delayed(shutil.copy)(i, self.workspace + self.raster_dir + "/" + os.path.split(i)[1]) for i in glob.glob(self.workspace + "LAS/" + folder + "/*.laz"))

        PL.utils.Run("lasindex -i " + self.workspace + self.raster_dir + "/*.laz -cores 50")
        PL.utils.Run("lastile -i " + self.workspace + self.raster_dir + "/*.laz -tile_size 1000 -buffer 25 -drop_class 0 -cores 45 -odir " + self.workspace + self.raster_dir + "/dalles -o " + self.workspace + self.raster_dir + "/dalles/MKP.laz")
        PL.utils.Run("lasthin -i " + self.workspace + self.raster_dir + "/dalles/*.laz " + thinning + " -cores 50 -odix _thin -olaz")
        PL.utils.Run("lastile -i " + self.workspace + self.raster_dir + "/dalles/*_thin.laz -remove_buffer -cores 50 -olaz")
        PL.utils.Run("lasmerge -i " + self.workspace + self.raster_dir + "/dalles/*_thin_1.laz -o " + self.workspace + "_".join(outName))
        shutil.rmtree(self.workspace + self.raster_dir)


if __name__ == '__main__':
    workspace = r'G:\RENNES1\Loire_totale_automne2019\Loire_Briare-Sully-sur-Loire\05-Traitements\Raster'+'//'
    a = Deliverable(workspace, 0.5, "Loire_zone45-4")
    #a.DTM("C2C3")
    #a.Density("C2C3")
    #a.DSM("C2C3", 'vegetation_building')
    #a.DCM("C2C3")
