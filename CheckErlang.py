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

from sets import Set
from pybeam import BeamFile

class lazy(object):
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, owner = None):
        if instance == None:
            return self
        val = self._function(instance)
        setattr(instance, self._function.func_name, val)
        return val

class CheckErlangImports(AbstractCheck.AbstractFilesCheck):
    def __init__(self, syspaths):
        AbstractCheck.AbstractFilesCheck.__init__(self, "CheckErlangImports", ".*?\.beam$")
        self._imports = dict()
        self._exports = Set()
        self.__file_re = re.compile(r'.*?\.beam')
        for syspath in syspaths:
            self.process_syspath(syspath)

    def process_syspath(self, syspath):
        for root, dirs, files in os.walk(syspath, followlinks=True):
            for beam in [BeamFile(x) for x in [os.path.join(root, filename) for filename in files] if self.__file_re.match(x)]:
                self.process_exports(beam)

    def process_exports(self, beam):
        thismodule = beam.modulename
        self._exports.update(Set(["%s:%s/%d" % (thismodule, function, arity) for (function, arity, label) in beam.exports]))

    def process_imports(self, beam, pkg, filename):
        self._imports[(pkg,filename)] = Set(["%s:%s/%d" % (module, function, arity) for (module, function, arity) in beam.imports])

    def check_file(self, pkg, filename):
        if not (pkg,filename) in self._imports:
            return

        imports = self._imports[(pkg,filename)]
        unresolved = imports.difference(self._exports)

        if not unresolved:
            return

        for mfa in unresolved:
            printWarning(pkg, "beam-import-not-found", filename, mfa)

class ErlangCheck(AbstractCheck.AbstractFilesCheck):
    def __init__(self):
        AbstractCheck.AbstractFilesCheck.__init__(self, "CheckErlang", ".*?\.beam$")
        build_dir = Config.getOption("Erlang.BuildDir", "^/home/abuild/.*")
        self.source_re = re.compile(build_dir)

    @lazy 
    def resolver(self):
        check_imports = CheckErlangImports(Config.getOption("Erlang.ErlangPaths", ["/usr/lib/erlang", "/usr/lib64/erlang"]))
        Config.addCheck("CheckErlangImports")
        return check_imports

    def check_file(self, pkg, filename):
        beam = BeamFile(pkg.files()[filename].path)
        if not 'debug_info' in beam.compileinfo['options']:
            printWarning(pkg, "beam-compiled-without-debug_info", filename)
        if 'time' in beam.compileinfo:
            printWarning(pkg, "beam-consists-compile-time", filename, str(beam.compileinfo['time']))
        if not self.source_re.match(beam.compileinfo['source'].value):
            printWarning(pkg, "beam-was-not-recompiled", filename, beam.compileinfo['source'].value)
        self.resolver.process_exports(beam)
        self.resolver.process_imports(beam, pkg, filename)

check=ErlangCheck()

if Config.info:
    addDetails(
'beam-compiled-without-debug_info',
"Your beam file indicates that it doesn't contain debug_info. Please, make sure that you compile with +debug_info.",
'beam-consists-compile-time',
"Your beam file consists compile time. Open Build Service may improperly consider it as changed."
'beam-was-not-recompiled',
"It seems that your beam file was not compiled by you, but was just copied in binary form to destination. Please, make sure that you really compile it from the sources.",
'beam-import-not-found',
"Your beam file imports the function which is not found in other beams, both system and yours. This will be possibly a reson for your application to crash. Please, check Requires:/BuildRequires: tags in your spec."
)

