import glob, os, pickle
from joblib import delayed, Parallel

import numpy as np

import plateforme_lidar as PL


class Overlap(object):
    def __init__(self, workspace, m3c2_file, out, settings=[]):
        # settings=[['standard,'LAS','Loire49-2'], rootNames, distUncertainty=0.02, m3c2_dist, lineNbLength=2]
        self.workspace = workspace
        self.m3c2File = m3c2_file
        self.out_name = out
        self.cc_options = settings[0]
        self.root_names_dict = settings[1]
        self.filter_dist_uncertainty = settings[2]
        self.m3c2_dist = settings[3]
        self.lineNbLength = settings[4]

        self.keys = list(self.root_names_dict.keys())
        self.root_length = len(self.root_names_dict[self.keys[0]][0])
        self._preprocessing_status = False
        self.file_list = []
        self.listCompareLines = []
        self.pairs_dict = []

    def _set_pairs_dict(self):
        self.pairs_dict = []
        pkl = os.path.join(self.workspace, "comparison.pkl")
        if os.path.exists(pkl):
            self.pairs_dict = pickle.load(open(pkl, 'rb'))
        else:
            lines = self.workspace + "*_thin.laz"
            self.pairs_dict = PL.calculs.select_pairs_overlap(lines, [self.root_length, self.lineNbLength])
            pickle.dump(self.pairs_dict, open(pkl, 'wb'))

    def _select_root(self, line_number):
        test = True
        compt = 0
        while test:
            if int(line_number) <= self.keys[compt]:
                test = False
            else:
                compt += 1
        root_name = self.root_names_dict[self.keys[compt]]
        return root_name[0] + line_number + root_name[1]

    def preprocessing(self):
        print("[Overlap] Pre-processing...")
        self.file_list = []
        self.listCompareLines = []
        self._set_pairs_dict()
        if len(self.pairs_dict.keys()) == 0:
            raise ValueError("Comparison dictionary is empty")

        for key in self.pairs_dict.keys():
            file_a = self._select_root(key)
            file_core_pts = file_a[0:-4] + "_thin.laz"
            for c in self.pairs_dict[key]:
                file_b = self._select_root(c)
                file_result = file_core_pts[0:-4] + "_m3c2_" + key + "and" + c + ".laz"
                self.file_list += [[file_a, file_b, file_core_pts, file_result]]
                self.listCompareLines += [key + "_" + c]
        self._preprocessing_status = True
        print("[Overlap] Pre-processing done !")

    def processing(self):
        if self._preprocessing_status:
            for i in range(0, len(self.file_list)):
                print("#=========================#")
                print("Comparison : " + self.listCompareLines[i])
                print("#=========================#")
                self.comparison(*self.file_list[i])

            print("[Overlap] M3C2 analyzing...")
            Parallel(n_jobs=20, verbose=1)(delayed(self.write_file)(self.workspace + self.file_list[i][-1]) for i in
                                           range(0, len(self.file_list)))
            query = "lasmerge -i " + self.workspace + "*_clean.laz -o " + self.workspace + self.out_name
            PL.utils.Run(query)
            print("[Overlap] M3C2 analyzing done !")

            [os.remove(i) for i in glob.glob(self.workspace + "*_thin.laz")]
            [os.remove(i) for i in glob.glob(self.workspace + "*_clean.laz")]
        else:
            raise OSError("Pre-processing your data before")

    def comparison(self, line_a, line_b, core_pts, out):
        query = PL.cloudcompare.open_file(self.cc_options,
                                          [self.workspace + line_a, self.workspace + line_b, self.workspace + core_pts])
        PL.cloudcompare.m3c2(query, self.workspace + self.m3c2File)
        PL.cloudcompare.last_file(self.workspace + core_pts[0:-4] + "_20*.laz", out)
        new_file = PL.cloudcompare.last_file(self.workspace + line_a[0:-4] + "_20*.laz")
        os.remove(new_file)
        new_file = PL.cloudcompare.last_file(self.workspace + line_a[0:-4] + "_M3C2_20*.laz")
        os.remove(new_file)
        new_file = PL.cloudcompare.last_file(self.workspace + line_b[0:-4] + "_20*.laz")
        os.remove(new_file)

    def write_file(self, filepath):
        in_data = PL.lastools.readLAS(filepath, extraField=True)
        select1 = in_data["distance_uncertainty"] < self.filter_dist_uncertainty
        select2 = np.logical_and(in_data["m3c2_distance"] < self.m3c2_dist, in_data["m3c2_distance"] > -self.m3c2_dist)
        select = np.logical_and(select1, select2)
        in_data2 = PL.lastools.Filter_LAS(in_data, select)
        extra = [(("m3c2_distance", "float32"), in_data2["m3c2_distance"]),
                 (("distance_uncertainty", "float32"),
                  in_data2["distance_uncertainty"])]

        PL.lastools.writeLAS(filepath[0:-4] + "_clean.laz", in_data2, extraField=extra)
