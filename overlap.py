import glob, os
import logging

import common_ple as ple


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def thin_lines(idir, odir, cores=None):
    if cores is None:
        cpu_count = os.cpu_count()
        print(f"cpu_count {cpu_count}")
        cores = max(1, int(cpu_count / 2))
    lines = glob.glob(os.path.join(idir, '*.laz'))
    logger.info(f'Found {len(lines)} line(s) to proceed')
    for line in lines:
        # -cores option not needed as we process the lines one by one
        ple.exe(f'lasthin -i {line} -step 1 -lowest -last_only -odir {odir} -odix _thin1_lastOnly -olaz')