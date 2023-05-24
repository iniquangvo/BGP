#################################################################################
##Script Header
# Copyright (c) 2022-2023 by Cisco Systems, Inc.
# Job file
#################################################################################

import os
from pyats.easypy import run
from pyats.datastructures.logic import Or

def main():

    script_path = os.path.join(os.path.dirname(__file__))
    testscript = os.path.join(script_path, 'bgp.py')
    datafile = os.path.join(script_path, 'data/bgp_datafile.yaml')
    run(testscript = testscript,datafile=datafile)   
    