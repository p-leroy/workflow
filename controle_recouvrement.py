# coding: utf-8
# Baptiste Feldmann

import glob, os, pickle
from joblib import delayed, Parallel

import numpy as np

import plateforme_lidar as PL


class Overlap(object):
    def __init__(self, workspace, m3c2_file, water_surface_file="", settings=[]):
        # settings=[['standard,'LAS','Loire49-2'],rootNames,distUncertainty=0.02,lineNbLength=2]
        self.workspace = workspace
        self.m3c2File = m3c2_file
        self.water_surface = water_surface_file
        self.cc_options = settings[0]
        self.root_names_dict = settings[1]
        self.filter_dist_uncertainty = settings[2]
        self.lineNbLength = settings[3]
        self.keyList = list(self.root_names_dict.keys())
        self.rootLength = len(self.root_names_dict[self.keyList[0]][0])
        self._preprocessingStatus = False
        self.folder = ""
        self.listFiles = []
        self.listCompareLines = []

    def _select_pairs(self, motif="*_thin.laz"):
        if os.path.exists(self.workspace + self.folder + "/comparison.pkl"):
            self.pairsDict = pickle.load(open(self.workspace + self.folder + "/comparison.pkl", 'rb'))
        else:
            self.pairsDict = PL.calculs.select_pairs_overlap(self.workspace + self.folder + "/" + motif,
                                                             [self.rootLength, self.lineNbLength])
            pickle.dump(self.pairsDict, open(self.workspace + self.folder + "/comparison.pkl", 'wb'))

    def _select_root_name(self, line_number):
        test = True
        compt = 0
        while test:
            if int(line_number) <= self.keyList[compt]:
                test = False
            else:
                compt += 1
        rootname = self.root_names_dict[self.keyList[compt]]
        return rootname[0] + line_number + rootname[1]

    def _filtering(self, workspace, inFile, outFile, filter_=[50, 0.2]):
        data = PL.lastools.readLAS(workspace + inFile, extraField=True)
        select = np.logical_or(data["c2c_absolute_distances"] > filter_[0],
                               data["c2c_absolute_distances_z"] > filter_[1])
        outData = PL.lastools.Filter_LAS(data, select)
        PL.lastools.writeLAS(workspace + outFile, outData)

    def preprocessing(self, folder):
        print("[Overlap] Pre-processing...")
        self.folder = folder
        self.listFiles = []
        self.listCompareLines = []
        if self.folder == "C2":
            self._select_pairs()
            if len(self.pairsDict.keys()) == 0:
                raise ValueError("Comparison dictionnary is empty")

            for i in self.pairsDict.keys():
                fileA = self._select_root_name(i)
                fileCorepts = fileA[0:-4] + "_thin.laz"
                for c in self.pairsDict[i]:
                    fileB = self._select_root_name(c)
                    fileResult = fileCorepts[0:-4] + "_m3c2_" + i + "and" + c + ".laz"
                    self.listFiles += [[fileA, fileB, fileCorepts, fileResult]]
                    self.listCompareLines += [i + "_" + c]

        elif self.folder == "C3":
            PL.cloudcompare.c2c_files(self.cc_options,
                                      self.workspace + self.folder + "/",
                                      [os.path.split(i)[1] for i in
                                       glob.glob(self.workspace + self.folder + "/*_C3_r_thin.laz")],
                                      self.workspace + self.water_surface, 10, 10)
            Parallel(n_jobs=20, verbose=1)(
                delayed(self._filtering)(self.workspace + self.folder + "/", i, i[0:-8] + "_1.laz") for i in
                [os.path.split(i)[1] for i in glob.glob(self.workspace + self.folder + "/*_C3_r_thin_C2C.laz")])
            for i in glob.glob(self.workspace + self.folder + "/*_C2C.laz"):
                os.remove(i)

            self._select_pairs(motif="*_thin_1.laz")
            if len(self.pairsDict.keys()) == 0:
                raise ValueError("Comparison dictionnary is empty")

            for i in self.pairsDict.keys():
                fileA = self._select_root_name(i)
                fileCorepts = fileA[0:-4] + "_thin_1.laz"
                for c in self.pairsDict[i]:
                    fileB = self._select_root_name(c)
                    fileResult = fileCorepts[0:-4] + "_m3c2_" + i + "and" + c + ".laz"
                    self.listFiles += [[fileA, fileB, fileCorepts, fileResult]]
                    self.listCompareLines += [i + "_" + c]

        elif self.folder == "C2_C3":
            PL.cloudcompare.c2c_files(self.cc_options,
                                      self.workspace + self.folder + "/",
                                      [os.path.split(i)[1] for i in
                                       glob.glob(self.workspace + self.folder + "/*_C2_r_thin.laz")],
                                      self.workspace + self.water_surface, 10, 10)
            Parallel(n_jobs=20, verbose=1)(
                delayed(self._filtering)(self.workspace + self.folder + "/", i, i[0:-8] + "_1.laz") for i in
                [os.path.split(i)[1] for i in glob.glob(self.workspace + self.folder + "/*_C2_r_thin_C2C.laz")])
            for i in glob.glob(self.workspace + self.folder + "/*_C2C.laz"):
                os.remove(i)

            for i in [os.path.split(i)[1] for i in glob.glob(self.workspace + self.folder + "/*_C2_r.laz")]:
                fileA = i
                fileCorepts = fileA[0:-4] + "_thin_1.laz"
                fileB = fileA[0:-9] + "_C3_r.laz"
                fileResult = fileCorepts[0:-4] + "_m3c2_C2C3.laz"
                self.listFiles += [[fileA, fileB, fileCorepts, fileResult]]
                self.listCompareLines += [i[self.rootLength:self.rootLength + self.lineNbLength]]
        else:
            raise OSError("Unknown folder")

        self._preprocessingStatus = True
        print("[Overlap] Pre-processing done !")

    def Processing(self):
        if self._preprocessingStatus:
            for i in range(0, len(self.listFiles)):
                print("#=========================#")
                print("Comparison : " + self.listCompareLines[i])
                print("#=========================#")
                self.Comparison(*self.listFiles[i])

            print("[Overlap] M3C2 analyzing...")
            self.results = Parallel(n_jobs=25, verbose=1)(
                delayed(self.AnalyzeFile)(self.workspace + self.folder + "/" + self.listFiles[i][-1],
                                          self.listCompareLines[i]) for i in range(0, len(self.listFiles)))
            np.savetxt(self.workspace + self.folder + "/save_results.txt", self.results, fmt='%s', delimiter=';',
                       header='Comparaison;moyenne (m);ecart-type (m)')
            print("[Overlap] M3C2 analyzing done !")
        else:
            raise OSError("Pre-processing your data before")

    def Comparison(self, lineA, lineB, corePts, outName):
        query = PL.cloudcompare.open_file(self.cc_options, [self.workspace + self.folder + "/" + lineA,
                                                            self.workspace + self.folder + "/" + lineB,
                                                            self.workspace + self.folder + "/" + corePts])
        PL.cloudcompare.m3c2(query, self.workspace + self.m3c2File)
        PL.cloudcompare.last_file(self.workspace + self.folder + "/" + corePts[0:-4] + "_20*.laz", outName)
        new_file = PL.cloudcompare.last_file(self.workspace + self.folder + "/" + lineA[0:-4] + "_20*.laz")
        os.remove(new_file)
        new_file = PL.cloudcompare.last_file(self.workspace + self.folder + "/" + lineA[0:-4] + "_M3C2_20*.laz")
        os.remove(new_file)
        new_file = PL.cloudcompare.last_file(self.workspace + self.folder + "/" + lineB[0:-4] + "_20*.laz")
        os.remove(new_file)

    def AnalyzeFile(self, filepath, compareID):
        inData = PL.lastools.readLAS(filepath, extraField=True)
        inData2 = PL.lastools.Filter_LAS(inData, np.logical_not(np.isnan(inData["distance_uncertainty"])))
        inData3 = PL.lastools.Filter_LAS(inData2, inData2["distance_uncertainty"] < self.filter_dist_uncertainty)
        m3c2_dist = inData3['m3c2_distance'][np.logical_not(np.isnan(inData3['m3c2_distance']))]

        if len(m3c2_dist) > 100:
            output = [compareID, np.round(np.mean(m3c2_dist), 3), np.round(np.std(m3c2_dist), 3)]
        else:
            output = [compareID, "NotEnoughPoints", "-"]
        return output
