# vim:sw=4:et
#############################################################################
# File          : CheckErlang.py
# Package       : rpmlint
# Author        : Matwey V. Kornilov
# Purpose       : Check for erlang compiled files
#############################################################################

from Filter import *
import AbstractCheck
import rpm
import re
import os
import commands
import Config
import stat

from pybeam import BeamFile

class ErlangCheck(AbstractCheck.AbstractFilesCheck):
    def __init__(self):
        AbstractCheck.AbstractFilesCheck.__init__(self, "CheckErlang", ".*?\.beam$")

    def check_file(self, pkg, filename):
        beam = BeamFile(pkg.files()[filename].path)
        if not 'debug_info' in beam.compileinfo['options']:
            printWarning(pkg, "beam-compiled-without-debug_info", filename)

check=ErlangCheck()

if Config.info:
    addDetails(
'beam-compiled-without-debug_info',
"Your beam file indicates that it doesn't contain debug_info. Please, make sure that you compile with +debug_info."
)
