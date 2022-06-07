# coding: utf-8
#
# formerly known as controle_recouvrement2.py [Baptiste Feldmann]

import glob, logging, os, pickle

import numpy as np
from joblib import Parallel,delayed

import plateforme_lidar as pl

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Overlap(object):
    def __init__(self, workspace, m3c2_file, water_surface="", settings=[]):

        self.workspace = workspace
        self.m3c2_file = m3c2_file
        self.water_surface = os.path.join(workspace, water_surface)

        self.cc_options = settings[0]
        self.root_names_dict = settings[1]
        self.max_uncertainty = settings[2]
        self.line_nb_digits = settings[3]

        self.keys = list(self.root_names_dict.keys())
        self.root_length = len(self.root_names_dict[self.keys[0]][0])
        self._preprocessingStatus = False

        self.folder = ""
        self.lines_dir = ""
        self.file_list = []
        self.pair_list = []
        self.overlapping_pairs = {}

    def _set_overlapping_pairs(self, pattern="*_thin.laz"):
        self.overlapping_pairs = []
        overlapping_pairs_pkl = os.path.join(self.lines_dir, "overlapping_pairs.pkl")
        if os.path.exists(overlapping_pairs_pkl):
            self.overlapping_pairs = pickle.load(open(overlapping_pairs_pkl, 'rb'))
        else:
            lines = os.path.join(self.lines_dir, pattern)  # only consider thin lines to investigate overlaps
            logger.info(f'self.root_length {self.root_length}, self.line_nb_digits {self.line_nb_digits}')
            self.overlapping_pairs, overlaps = pl.calculs.select_pairs_overlap(lines, [self.root_length, self.line_nb_digits])
            pickle.dump(self.overlapping_pairs, open(overlapping_pairs_pkl, 'wb'))
            overlaps_pkl = os.path.join(self.lines_dir, "overlaps.pkl")
            pickle.dump(overlaps, open(overlaps_pkl, 'wb'))

    def _get_name_from_line_number(self, line_number):
        test = True
        compt = 0
        while test:
            if int(line_number) <= self.keys[compt]:
                test = False
            else:
                compt += 1
        rootname = self.root_names_dict[self.keys[compt]]
        return rootname[0] + line_number + rootname[1]

    def _filtering_c2c(self, in_file, out_file, c2c=50, c2c_z=0.2):
        head, tail = os.path.split(in_file)
        data = pl.lastools.ReadLAS(in_file, extraField=True)

        try:  # C2C absolute distances
            select_c2c = data["c2c__absolute__distances"] > c2c
        except KeyError:
            raise KeyError(f"c2c__absolute__distances is not in the extra_fields list")
        try:  # C2C absolute distances Z
            select_c2c_z = data["c2c__absolute__distances__z"] > c2c_z
        except KeyError:
            raise KeyError(f"c2c__absolute__distances__z is not in the extra_fields list")
        select = select_c2c | select_c2c_z

        out_data = pl.lastools.Filter_LAS(data, select)
        out = os.path.join(head, out_file)
        pl.lastools.WriteLAS(out, out_data)
        return out

    def preprocessing(self, folder, pattern="*_thin.laz", c3_pattern="3_s.laz"):
        print(f"[Overlap.preprocessing] folder: {folder}")

        self.folder = folder
        self.file_list = []
        self.pair_list = []

        self.lines_dir = os.path.join(self.workspace, self.folder)

        if self.folder == "C2":  # ***  C2 *** #
            self._set_overlapping_pairs(pattern=pattern)
            if self.overlapping_pairs is not {}:
                for num_a in self.overlapping_pairs.keys():
                    file_a = self._get_name_from_line_number(num_a)
                    file_core_pts = file_a[0:-4] + "_thin.laz"
                    for num_b in self.overlapping_pairs[num_a]:
                        file_b = self._get_name_from_line_number(num_b)
                        file_result = file_core_pts[0:-4] + "_m3c2_" + num_a + "and" + num_b + ".laz"
                        self.file_list += [[file_a, file_b, file_core_pts, file_result]]
                        self.pair_list += [num_a + "_" + num_b]
            else:
                raise ValueError("Overlapping pairs dictionary is empty")

        elif self.folder == "C3":  # *** C3 *** #
            c3_thin_files = glob.glob(os.path.join(self.lines_dir, "*_thin.laz"))
            octree_lvl = 10
            nbr_job = 10
            # pl.cloudcompare.c2c_files(self.cc_options,
            #                           c3_thin_files,
            #                           self.water_surface,
            #                           octree_lvl=octree_lvl,
            #                           nbr_job=nbr_job)

            thin_c2c_files = glob.glob(os.path.join(self.lines_dir, "*_thin_C2C.laz"))
            Parallel(n_jobs=20, verbose=1)(
                delayed(self._filtering_c2c)(file, file[0:-8] + "_1.laz")
                for file in thin_c2c_files
            )

            for file in glob.glob(os.path.join(self.lines_dir, "*_C2C.laz")):
                os.remove(file)

            self._set_overlapping_pairs(pattern="*_thin.laz")
            if self.overlapping_pairs is {}:
                raise ValueError("Overlapping pairs dictionary is empty")
            for num_a in self.overlapping_pairs.keys():
                file_a = self._get_name_from_line_number(num_a)
                file_core_pts =  file_a[0:-4] + "_thin.laz"
                for num_b in self.overlapping_pairs[num_a]:
                    file_b = self._get_name_from_line_number(num_b)
                    file_result = file_core_pts[0:-4] + "_m3c2_" + num_a + "and" + num_b + ".laz"
                    self.file_list += [[file_a, file_b, file_core_pts, file_result]]
                    self.pair_list += [num_a + "_" + num_b]

        elif self.folder == "C2_C3":  # *** C2_C3 *** #
            # c2_thin_files = glob.glob(os.path.join(self.lines_dir, "*_thin.laz"))
            # octree_lvl = 10
            # nbr_job = 10
            # pl.cloudcompare.c2c_files(self.cc_options,
            #                           c2_thin_files,
            #                           self.water_surface,
            #                           octree_lvl=octree_lvl,
            #                           nbr_job=nbr_job)
            #
            # thin_c2c_files = glob.glob(os.path.join(self.lines_dir, "*_thin_C2C.laz"))
            # Parallel(n_jobs=20, verbose=1)(
            #     delayed(self._filtering_c2c)(file, file[0:-8] + "_core.laz")
            #     for file in thin_c2c_files
            # )
            # for i in glob.glob(os.path.join(self.lines_dir, "*_C2C.laz")):
            #     os.remove(i)

            thin_core_files = glob.glob(os.path.join(self.lines_dir, "*_thin_core.laz"))
            for file_core in thin_core_files:
                file_a = file_core[0:-14] + '.laz'
                file_b = file_core[0:-17] + c3_pattern
                file_result = file_core[0:-4] + "_m3c2_C2C3.laz"
                self.file_list += [[file_a, file_b, file_core, file_result]]
                self.pair_list += file_core

        else:
            raise OSError("Unknown folder")
        
        self._preprocessingStatus = True
        print("[Overlap.preprocessing] done")

        return self.file_list

    def processing(self):
        if self._preprocessingStatus:
            for i in range(0, len(self.file_list)):
                print("[Overlap.processing] Measure distances between lines with M3C2: " + self.pair_list[i])
                self.measure_distances_with_m3c2(*self.file_list[i])
                    
            print("[Overlap.processing] M3C2 analyzes")
            self.results = Parallel(n_jobs=25, verbose=1)(
                delayed(self.filter_m3c2_data)(
                    os.path.join(self.lines_dir, elem[-1]), self.pair_list[count])
                for count, elem in enumerate(self.file_list)
            )
            np.savetxt(os.path.join(self.lines_dir, "save_results.txt"), self.results,
                       fmt='%s', delimiter=';', header='Comparaison;moyenne (m);ecart-type (m)')
            print("[Overlap.processing] M3C2 analyzes done")
        else:
            raise OSError("[Overlap.processing] Preprocessing not done!")

    def measure_distances_with_m3c2(self, line_a, line_b, core_pts, out):
        path_a = os.path.join(self.lines_dir, line_a)
        # do the files exist?
        if not os.path.exists(path_a):
            raise FileNotFoundError
        path_b = os.path.join(self.lines_dir, line_b)
        if not os.path.exists(path_b):
            raise FileNotFoundError
        path_core_pts = os.path.join(self.lines_dir, core_pts)
        if not os.path.exists(path_core_pts):
            raise FileNotFoundError
        m3c2_params = os.path.join(self.lines_dir, self.m3c2_file)
        if not os.path.exists(m3c2_params):
            raise FileNotFoundError

        query = pl.cloudcompare.open_file(self.cc_options, [path_a, path_b, path_core_pts])
        pl.cloudcompare.m3c2(query, m3c2_params)
        root, ext = os.path.splitext(path_a)
        m3c2_expected_out = root + '_M3C2.laz'
        head, tail = os.path.split(path_a)
        dst = os.path.join(head, out)
        if os.path.exists(dst):
            os.remove(dst)
            print(f'[Overlap.measure_distances_with_m3c2] remove {dst}')
        try:
            os.rename(m3c2_expected_out, dst)
            print(f'{m3c2_expected_out} renamed to {out}')
        except OSError as error:
            print(error)

    def filter_m3c2_data(self, filepath, compare_id):
        # filter distance uncertainty
        in_data = pl.lastools.ReadLAS(filepath, extraField=True)
        selection = ~(np.isnan(in_data["distance__uncertainty"]))
        in_data2 = pl.lastools.Filter_LAS(in_data, selection)
        selection = in_data2["distance__uncertainty"] < self.max_uncertainty
        in_data3 = pl.lastools.Filter_LAS(in_data2, selection)
        # filter M3C2 distance
        selection = ~(np.isnan(in_data3['m3c2__distance']))
        m3c2_dist = in_data3['m3c2__distance'][selection]

        if len(m3c2_dist) > 100:
            output = [compare_id, np.round(np.mean(m3c2_dist), 3), np.round(np.std(m3c2_dist), 3)]
        else:
            output = [compare_id, "NotEnoughPoints", "-"]
        return output
