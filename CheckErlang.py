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

buildin_exports = Set(['binary:at/2', 'binary:bin_to_list/1', 'binary:bin_to_list/2',
'binary:bin_to_list/3', 'binary:compile_pattern/1', 'binary:copy/1',
'binary:copy/2', 'binary:decode_unsigned/1', 'binary:decode_unsigned/2',
'binary:encode_unsigned/1', 'binary:encode_unsigned/2', 'binary:first/1',
'binary:last/1', 'binary:list_to_bin/1', 'binary:longest_common_prefix/1',
'binary:longest_common_suffix/1', 'binary:match/2', 'binary:match/3',
'binary:matches/2', 'binary:matches/3', 'binary:part/2', 'binary:part/3',
'binary:referenced_byte_size/1', 'code:get_chunk/2', 'code:is_module_native/1',
'code:make_stub_module/3', 'code:module_md5/1', 'erlang:-/1', 'erlang:+/1',
'erlang:</2', 'erlang:=</2', 'erlang:==/2', 'erlang:=:=/2', 'erlang:=/=/2',
'erlang:>=/2', 'erlang:>/2', 'erlang:--/2', 'erlang:-/2', 'erlang:!/2',
'erlang:/=/2', 'erlang://2', 'erlang:*/2', 'erlang:+/2', 'erlang:++/2',
'erlang:abs/1', 'erlang:adler32/1', 'erlang:adler32/2',
'erlang:adler32_combine/3', 'erlang:and/2', 'erlang:append/2',
'erlang:append_element/2', 'erlang:apply/3', 'erlang:atom_to_binary/2',
'erlang:atom_to_list/1', 'erlang:band/2', 'erlang:binary_part/2',
'erlang:binary_part/3', 'erlang:binary_to_atom/2',
'erlang:binary_to_existing_atom/2', 'erlang:binary_to_float/1',
'erlang:binary_to_integer/1', 'erlang:binary_to_integer/2',
'erlang:binary_to_list/1', 'erlang:binary_to_list/3', 'erlang:binary_to_term/1',
'erlang:binary_to_term/2', 'erlang:bit_size/1', 'erlang:bitstring_to_list/1',
'erlang:bnot/1', 'erlang:bor/2', 'erlang:bsl/2', 'erlang:bsr/2',
'erlang:bump_reductions/1', 'erlang:bxor/2', 'erlang:byte_size/1',
'erlang:call_on_load_function/1', 'erlang:cancel_timer/1',
'erlang:check_old_code/1', 'erlang:check_process_code/2', 'erlang:crc32/1',
'erlang:crc32/2', 'erlang:crc32_combine/3', 'erlang:date/0',
'erlang:decode_packet/3', 'erlang:delete_element/2', 'erlang:delete_module/1',
'erlang:demonitor/1', 'erlang:demonitor/2', 'erlang:display/1',
'erlang:display_nl/0', 'erlang:display_string/1', 'erlang:dist_exit/3',
'erlang:div/2', 'erlang:dt_append_vm_tag_data/1', 'erlang:dt_get_tag/0',
'erlang:dt_get_tag_data/0', 'erlang:dt_prepend_vm_tag_data/1',
'erlang:dt_put_tag/1', 'erlang:dt_restore_tag/1', 'erlang:dt_spread_tag/1',
'erlang:element/2', 'erlang:erase/0', 'erlang:erase/1', 'erlang:error/1',
'erlang:error/2', 'erlang:exit/1', 'erlang:exit/2', 'erlang:external_size/1',
'erlang:external_size/2', 'erlang:finish_after_on_load/2',
'erlang:finish_loading/1', 'erlang:float/1', 'erlang:float_to_binary/1',
'erlang:float_to_binary/2', 'erlang:float_to_list/1', 'erlang:float_to_list/2',
'erlang:function_exported/3', 'erlang:fun_info/2', 'erlang:fun_to_list/1',
'erlang:garbage_collect/0', 'erlang:garbage_collect/1', 'erlang:get/0',
'erlang:get/1', 'erlang:get_keys/1', 'erlang:get_module_info/1',
'erlang:get_module_info/2', 'erlang:get_stacktrace/0', 'erlang:group_leader/0',
'erlang:group_leader/2', 'erlang:halt/0', 'erlang:halt/1', 'erlang:halt/2',
'erlang:hash/2', 'erlang:hd/1', 'erlang:hibernate/3', 'erlang:insert_element/3',
'erlang:integer_to_binary/1', 'erlang:integer_to_list/1',
'erlang:iolist_size/1', 'erlang:iolist_to_binary/1', 'erlang:is_alive/0',
'erlang:is_atom/1', 'erlang:is_binary/1', 'erlang:is_bitstring/1',
'erlang:is_boolean/1', 'erlang:is_builtin/3', 'erlang:is_float/1',
'erlang:is_function/1', 'erlang:is_function/2', 'erlang:is_integer/1',
'erlang:is_list/1', 'erlang:is_number/1', 'erlang:is_pid/1', 'erlang:is_port/1',
'erlang:is_process_alive/1', 'erlang:is_record/2', 'erlang:is_record/3',
'erlang:is_reference/1', 'erlang:is_tuple/1', 'erlang:length/1',
'erlang:link/1', 'erlang:list_to_atom/1', 'erlang:list_to_binary/1',
'erlang:list_to_bitstring/1', 'erlang:list_to_existing_atom/1',
'erlang:list_to_float/1', 'erlang:list_to_integer/1',
'erlang:list_to_integer/2', 'erlang:list_to_pid/1', 'erlang:list_to_tuple/1',
'erlang:loaded/0', 'erlang:load_nif/2', 'erlang:localtime/0',
'erlang:localtime_to_universaltime/2', 'erlang:make_fun/3', 'erlang:make_ref/0',
'erlang:make_tuple/2', 'erlang:make_tuple/3', 'erlang:match_spec_test/3',
'erlang:md5/1', 'erlang:md5_final/1', 'erlang:md5_init/0',
'erlang:md5_update/2', 'erlang:module_loaded/1', 'erlang:monitor/2',
'erlang:monitor_node/2', 'erlang:monitor_node/3', 'erlang:nif_error/1',
'erlang:nif_error/2', 'erlang:node/0', 'erlang:node/1', 'erlang:nodes/1',
'erlang:not/1', 'erlang:now/0', 'erlang:open_port/2', 'erlang:or/2',
'erlang:phash/2', 'erlang:phash2/1', 'erlang:phash2/2', 'erlang:pid_to_list/1',
'erlang:ports/0', 'erlang:port_to_list/1',
'erlang:posixtime_to_universaltime/1', 'erlang:pre_loaded/0',
'erlang:prepare_loading/2', 'erlang:process_display/2', 'erlang:processes/0',
'erlang:process_flag/2', 'erlang:process_flag/3', 'erlang:process_info/1',
'erlang:process_info/2', 'erlang:purge_module/1', 'erlang:put/2',
'erlang:raise/3', 'erlang:read_timer/1', 'erlang:ref_to_list/1',
'erlang:register/2', 'erlang:registered/0', 'erlang:rem/2',
'erlang:resume_process/1', 'erlang:round/1', 'erlang:self/0', 'erlang:send/2',
'erlang:send/3', 'erlang:send_after/3', 'erlang:seq_trace/2',
'erlang:seq_trace_info/1', 'erlang:seq_trace_print/1',
'erlang:seq_trace_print/2', 'erlang:setelement/3', 'erlang:setnode/2',
'erlang:setnode/3', 'erlang:size/1', 'erlang:spawn/3', 'erlang:spawn_link/3',
'erlang:spawn_opt/1', 'erlang:split_binary/2', 'erlang:start_timer/3',
'erlang:statistics/1', 'erlang:subtract/2', 'erlang:suspend_process/2',
'erlang:system_flag/2', 'erlang:system_info/1', 'erlang:system_monitor/0',
'erlang:system_monitor/1', 'erlang:system_monitor/2', 'erlang:system_profile/0',
'erlang:system_profile/2', 'erlang:term_to_binary/1', 'erlang:term_to_binary/2',
'erlang:throw/1', 'erlang:time/0', 'erlang:tl/1', 'erlang:trace/3',
'erlang:trace_delivered/1', 'erlang:trace_info/2', 'erlang:trace_pattern/2',
'erlang:trace_pattern/3', 'erlang:trunc/1', 'erlang:tuple_size/1',
'erlang:tuple_to_list/1', 'erlang:universaltime/0',
'erlang:universaltime_to_localtime/1', 'erlang:universaltime_to_posixtime/1',
'erlang:unlink/1', 'erlang:unregister/1', 'erlang:whereis/1', 'erlang:xor/2',
'erl_ddll:demonitor/1', 'erl_ddll:format_error_int/1', 'erl_ddll:info/2',
'erl_ddll:loaded_drivers/0', 'erl_ddll:monitor/2', 'erl_ddll:try_load/3',
'erl_ddll:try_unload/2', 'error_logger:warning_map/0',
'erts_debug:breakpoint/2', 'erts_debug:disassemble/1', 'erts_debug:display/1',
'erts_debug:dist_ext_to_term/2', 'erts_debug:dump_links/1',
'erts_debug:dump_monitors/1', 'erts_debug:flat_size/1',
'erts_debug:get_internal_state/1', 'erts_debug:instructions/0',
'erts_debug:lock_counters/1', 'erts_debug:same/2',
'erts_debug:set_internal_state/2', 'erts_internal:port_call/3',
'erts_internal:port_close/1', 'erts_internal:port_command/3',
'erts_internal:port_connect/2', 'erts_internal:port_control/3',
'erts_internal:port_get_data/1', 'erts_internal:port_info/1',
'erts_internal:port_info/2', 'erts_internal:port_set_data/2', 'ets:all/0',
'ets:delete/1', 'ets:delete/2', 'ets:delete_all_objects/1',
'ets:delete_object/2', 'ets:first/1', 'ets:give_away/3', 'ets:info/1',
'ets:info/2', 'ets:insert/2', 'ets:insert_new/2', 'ets:is_compiled_ms/1',
'ets:last/1', 'ets:lookup/2', 'ets:lookup_element/3', 'ets:match/1',
'ets:match/2', 'ets:match/3', 'ets:match_object/1', 'ets:match_object/2',
'ets:match_object/3', 'ets:match_spec_compile/1', 'ets:match_spec_run_r/3',
'ets:member/2', 'ets:new/2', 'ets:next/2', 'ets:prev/2', 'ets:rename/2',
'ets:safe_fixtable/2', 'ets:select/1', 'ets:select/2', 'ets:select/3',
'ets:select_count/2', 'ets:select_delete/2', 'ets:select_reverse/1',
'ets:select_reverse/2', 'ets:select_reverse/3', 'ets:setopts/2', 'ets:slot/2',
'ets:update_counter/3', 'ets:update_element/3', 'file:native_name_encoding/0',
'io:printable_range/0', 'lists:keyfind/3', 'lists:keymember/3',
'lists:keysearch/3', 'lists:member/2', 'lists:reverse/2', 'math:acos/1',
'math:acosh/1', 'math:asin/1', 'math:asinh/1', 'math:atan/1', 'math:atan2/2',
'math:atanh/1', 'math:cos/1', 'math:cosh/1', 'math:erf/1', 'math:erfc/1',
'math:exp/1', 'math:log/1', 'math:log10/1', 'math:pow/2', 'math:sin/1',
'math:sinh/1', 'math:sqrt/1', 'math:tan/1', 'math:tanh/1',
'net_kernel:dflag_unicode_io/1', 'os:getenv/0', 'os:getenv/1', 'os:getpid/0',
'os:putenv/2', 'os:timestamp/0', 'prim_file:internal_name2native/1',
'prim_file:internal_native2name/1', 'prim_file:internal_normalize_utf8/1',
'prim_file:is_translatable/1', 're:compile/1', 're:compile/2', 're:run/2',
're:run/3', 'string:to_float/1', 'string:to_integer/1', 'unicode:bin_is_7bit/1',
'unicode:characters_to_binary/2', 'unicode:characters_to_list/2',])

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
        self._exports = buildin_exports
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

