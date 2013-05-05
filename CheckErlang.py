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
        build_dir = Config.getOption("Erlang.BuildDir", "^/home/abuild/.*")
        self.source_re = re.compile(build_dir)

    def check_file(self, pkg, filename):
        beam = BeamFile(pkg.files()[filename].path)
        if not 'debug_info' in beam.compileinfo['options']:
            printWarning(pkg, "beam-compiled-without-debug_info", filename)
        if 'time' in beam.compileinfo:
            printWarning(pkg, "beam-consists-compile-time", filename, str(beam.compileinfo['time']))
        if not self.source_re.match(beam.compileinfo['source'].value):
            printWarning(pkg, "beam-was-not-recompiled", filename, beam.compileinfo['source'].value)

check=ErlangCheck()

if Config.info:
    addDetails(
'beam-compiled-without-debug_info',
"Your beam file indicates that it doesn't contain debug_info. Please, make sure that you compile with +debug_info.",
'beam-consists-compile-time',
"Your beam file consists compile time. Open Build Service may improperly consider it as changed.",
'beam-was-not-recompiled',
"It seems that your beam file was not compiled by you, but was just copied in binary form to destination. Please, make sure that you really compile it from the sources."
)

