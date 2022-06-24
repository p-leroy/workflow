import os

import numpy as np

import tools.cc as cc

idir = r'C:\DATA\Clouds2022'
pc1, sf1, config1 = cc.read_sbf(os.path.join(idir, 'pc1.sbf'))
pc2, sf2, config2 = cc.read_sbf(os.path.join(idir, 'pc2.sbf'))

shift = np.mean(pc1, axis=0).reshape(1, -1)
pc1 -= shift
pc2 -= shift

config1['SBF']['GlobalShift'] = '0., 0., 0.'
cc.write_sbf(os.path.join(idir, 'pc1_centered.sbf'), pc1, sf1, config1)
cc.write_sbf(os.path.join(idir, 'pc2_centered.sbf'), pc2, sf2, config1)
