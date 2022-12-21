# ============================================================
#
# LLVM IL Parser.
#
# Author:   Bill Mahoney
# Grammar:  http://lists.llvm.org/pipermail/llvm-dev/2018-June/123851.html
# Based on: https://www.dabeaz.com/ply/example.html
#
# ============================================================
#
# The grammar I started with is based on the above references, which
# came from looking at the original LLVM C++ code. But the actual C++
# code has places where it is forgiving, epends on trailing context,
# and so on. Many of these were encountered when compiling the SPEC
# CPU benchmarks and the grammar was corrected as I went along. These
# corrections are noted in a corresponding Word doc and in comments
# below at the actual productions involved.
#
# ============================================================

import sys
import os

# Put "ply" under this directory and put a (full) pathname to it.
sys.path.append('/Users/billmahoney/Dropbox/Projects/LLVM_CWE/ply-3.11')

import ply.lex as lex
import ply.yacc as yacc
import logging

# I never quite figured out how to move the line number information
# from the lexical analysis into the parser side of things. So this
# is a hack that I'm sure could be better.
line_number = 0
number_of_errors = 0

reserved = {
    "acq_rel" : "acq_rel",
    "acquire" : "acquire",
    "add" : "add",
    "addrspace" : "addrspace",
    "addrspacecast" : "addrspacecast",
    "afn" : "afn",
#   "alias" : "alias",
    "align" : "align",
    "align:" : "align_colon",
    "alignstack" : "alignstack",
    "alloca" : "alloca",
    "allocsize" : "allocsize",
    "alwaysinline" : "alwaysinline",
    "amdgpu_cs" : "amdgpu_cs",
    "amdgpu_es" : "amdgpu_es",
    "amdgpu_gs" : "amdgpu_gs",
    "amdgpu_hs" : "amdgpu_hs",
    "amdgpu_kernel" : "amdgpu_kernel",
    "amdgpu_ls" : "amdgpu_ls",
    "amdgpu_ps" : "amdgpu_ps",
    "amdgpu_vs" : "amdgpu_vs",
    "and" : "and_kw",
#   "any" : "any",
    "anyregcc" : "anyregcc",
#   "appending" : "appending",
    "arcp" : "arcp",
    "arg:" : "arg_colon",
    "argmemonly" : "argmemonly",
    "arm_aapcscc" : "arm_aapcscc",
    "arm_aapcs_vfpcc" : "arm_aapcs_vfpcc",
    "arm_apcscc" : "arm_apcscc",
    "ashr" : "ashr",
    "asm" : "asm_kw",
    "atomic" : "atomic",
    "atomicrmw" : "atomicrmw",
#   "attributes" : "attributes",
    "attributes:" : "attributes_colon",
#   "available_externally" : "available_externally",
    "avr_intrcc" : "avr_intrcc",
    "avr_signalcc" : "avr_signalcc",
    "baseType:" : "baseType_colon",
    "bitcast" : "bitcast",
    "blockaddress" : "blockaddress",
#   "br" : "br",
    "builtin" : "builtin",
    "byval" : "byval",
    "call" : "call",
#   "caller" : "caller",
    "catch" : "catch",
    "catchpad" : "catchpad",
#   "catchret" : "catchret",
#   "catchswitch" : "catchswitch",
    "cc" : "cc",
    "ccc" : "ccc",
    "cc:" : "cc_colon",
    "checksum:" : "checksum_colon",
    "checksumkind:" : "checksumkind_colon",
    "cleanup" : "cleanup",
    "cleanuppad" : "cleanuppad",
#   "cleanupret" : "cleanupret",
    "cmpxchg" : "cmpxchg",
    "coldcc" : "coldcc",
    "cold" : "cold",
    "column:" : "column_colon",
#   "comdat" : "comdat",
#   "common" : "common",
#   "constant" : "constant",
    "containingType:" : "containingType_colon",
    "contract" : "contract",
    "convergent" : "convergent",
    "count:" : "count_colon",
    "cxx_fast_tlscc" : "cxx_fast_tlscc",
#   "datalayout" : "datalayout",
    "debugInfoForProfiling:" : "debugInfoForProfiling_colon",
    "declaration:" : "declaration_colon",
#   "declare" : "declare",
#   "default" : "default_kw",
#   "define" : "define",
    "dereferenceable" : "dereferenceable",
    "dereferenceable_or_null" : "dereferenceable_or_null",
    "directory:" : "directory_colon",
    "discriminator:" : "discriminator_colon",
#   "distinct" : "distinct",
#   "dllexport" : "dllexport",
#   "dllimport" : "dllimport",
    "double" : "double_kw",
#   "dso_local" : "dso_local",
#   "dso_preemptable" : "dso_preemptable",
    "dwarfAddressSpace:" : "dwarfAddressSpace_colon",
    "dwoid:" : "dwoId_colon",
    "elements:" : "elements_colon",
    "..." : "elipsis",
    "emissionKind:" : "emissionKind_colon",
    "encoding:" : "encoding_colon",
    "entity:" : "entity_colon",
    "enums:" : "enums_colon",
    "eq" : "eq",
    "exact" : "exact",
#   "exactmatch" : "exactmatch",
    "exportSymbols:" : "exportSymbols_colon",
    "expr:" : "expr_colon",
#   "external" : "external",
#   "externally_initialized" : "externally_initialized",
#   "extern_weak" : "extern_weak",
    "extractelement" : "extractelement",
    "extractvalue" : "extractvalue",
    "extraData:" : "extraData_colon",
    "fadd" : "fadd",
    "false" : "false_kw",
    "fastcc" : "fastcc",
    "fast" : "fast",
    "fcmp" : "fcmp",
    "fdiv" : "fdiv",
    "fence" : "fence",
    "file:" : "file_colon",
    "filename:" : "filename_colon",
    "filter" : "filter",
    "flags:" : "flags_colon",
    "float" : "float_kw",
    "fmul" : "fmul",
    "fp128" : "fp128",
    "fpext" : "fpext",
    "fptosi" : "fptosi",
    "fptoui" : "fptoui",
    "fptrunc" : "fptrunc",
    "frem" : "frem",
#   "from" : "from",
    "fsub" : "fsub",
    "FullDebug" : "FullDebug",
#   "gc" : "gc",
    "getelementptr" : "getelementptr",
    "getter:" : "getter_colon",
    "ghccc" : "ghccc",
#   "global" : "global",
    "globals:" : "globals_colon",
    "gnuPubnames:" : "gnuPubnames_colon",
    "half" : "half",
    "hhvm_ccc" : "hhvm_ccc",
    "hhvmcc" : "hhvmcc",
#   "hidden" : "hidden",
    "icmp" : "icmp",
    "identifier:" : "identifier_colon",
#   "ifunc" : "ifunc",
    "immarg" : "immarg", # Appeared in version 9.01
    "imports:" : "imports_colon",
    "inaccessiblememonly" : "inaccessiblememonly",
    "inaccessiblemem_or_argmemonly" : "inaccessiblemem_or_argmemonly",
    "inalloca" : "inalloca",
    "inbounds" : "inbounds",
#   "indirectbr" : "indirectbr",
#   "initialexec" : "initialexec",
    "inlinedAt:" : "inlinedAt_colon",
    "inlinehint" : "inlinehint",
    "inrange" : "inrange",
    "inreg" : "inreg",
    "insertelement" : "insertelement",
    "insertvalue" : "insertvalue",
    "inteldialect" : "inteldialect",
    "intel_ocl_bicc" : "intel_ocl_bicc",
#   "internal" : "internal",
    "inttoptr" : "inttoptr",
#   "invoke" : "invoke",
    "isDefinition:" : "isDefinition_colon",
    "isLocal:" : "isLocal_colon",
    "isOptimized:" : "isOptimized_colon",
    "isUnsigned:" : "isUnsigned_colon",
    "jumptable" : "jumptable",
#   "kludge_case_here" : "kludge_case_here", # See word document..
    "label" : "label",
    "landingpad" : "landingpad",
    "language:" : "language_colon",
#   "largest" : "largest",
    "line:" : "line_colon",
    "LineTablesOnly" : "LineTablesOnly",
    "linkageName:" : "linkageName_colon",
#   "linkonce" : "linkonce",
#   "linkonce_odr" : "linkonce_odr",
    "load" : "load",
#   "localdynamic" : "localdynamic",
#   "localexec" : "localexec",
#   "local_unnamed_addr" : "local_unnamed_addr",
    "lowerBound:" : "lowerBound_colon",
    "lshr" : "lshr",
    "macros:" : "macros_colon",
    "max" : "max",
    "metadata" : "metadata",
    "min" : "min",
    "minsize" : "minsize",
#   "module" : "module",
    "monotonic" : "monotonic",
    "msp430_intrcc" : "msp430_intrcc",
    "mul" : "mul",
    "musttail" : "musttail",
    "naked" : "naked",
    "name:" : "name_colon",
    "nameTableKind:" : "nameTableKind_colon", # Not in original, needed by DICompileUnitFieldList
    "nand" : "nand",
    "ne" : "ne",
    "nest" : "nest",
    "ninf" : "ninf",
    "nnan" : "nnan",
    "noalias" : "noalias",
    "nobuiltin" : "nobuiltin",
    "nocapture" : "nocapture",
    "NoDebug" : "NoDebug",
    "nodes:" : "nodes_colon",
    "noduplicate" : "noduplicate",
#   "noduplicates" : "noduplicates",
    "nofree" : "nofree", # LLVM grammar, seems to appear with verison 9
    "noimplicitfloat" : "noimplicitfloat",
    "noinline" : "noinline",
    "none" : "none",
    "nonlazybind" : "nonlazybind",
    "nonnull" : "nonnull",
    "norecurse" : "norecurse",
    "noredzone" : "noredzone",
    "noreturn" : "noreturn",
    "notail" : "notail",
    "nounwind" : "nounwind",
    "nsw" : "nsw",
    "nsz" : "nsz",
    "null" : "null",
    "nuw" : "nuw",
    "oeq" : "oeq",
    "offset:" : "offset_colon",
    "oge" : "oge",
    "ogt" : "ogt",
    "ole" : "ole",
    "olt" : "olt",
    "one" : "one",
#   "opaque" : "opaque",
    "optnone" : "optnone",
    "optsize" : "optsize",
    "ord" : "ord",
    "or" : "or_kw",
#   "personality" : "personality",
    "phi" : "phi",
    "ppc_fp128" : "ppc_fp128",
#   "prefix" : "prefix",
    "preserve_allcc" : "preserve_allcc",
    "preserve_mostcc" : "preserve_mostcc",
#   "private" : "private",
    "producer:" : "producer_colon",
#   "prologue" : "prologue",
#   "protected" : "protected",
    "ptr" : "ptr",                 # Needed suddenly for LLVM 15 - see p_PointerType
    "ptrtoint" : "ptrtoint",
    "ptx_device" : "ptx_device",
    "ptx_kernel" : "ptx_kernel",
    "readnone" : "readnone",
    "readonly" : "readonly",
    "reassoc" : "reassoc",
    "release" : "release",
#   "resume" : "resume",
    "retainedNodes:" : "retainedNodes_colon",
    "retainedTypes:" : "retainedTypes_colon",
#   "ret" : "ret",
    "returned" : "returned",
    "returns_twice" : "returns_twice",
    "runtimeLang:" : "runtimeLang_colon",
    "runtimeVersion:" : "runtimeVersion_colon",
    "safestack" : "safestack",
#   "samesize" : "samesize",
    "sanitize_address" : "sanitize_address",
    "sanitize_hwaddress" : "sanitize_hwaddress",
    "sanitize_memory" : "sanitize_memory",
    "sanitize_thread" : "sanitize_thread",
    "scope:" : "scope_colon",
    "scopeLine:" : "scopeLine_colon",
    "sdiv" : "sdiv",
#   "section" : "section",
    "select" : "select",
    "seq_cst" : "seq_cst",
    "setter:" : "setter_colon",
    "sext" : "sext",
    "sge" : "sge",
    "sgt" : "sgt",
    "shl" : "shl",
    "shufflevector" : "shufflevector",
    "sideeffect" : "sideeffect",
    "signext" : "signext",
    "sitofp" : "sitofp",
    "size:" : "size_colon",
    "sle" : "sle",
    "slt" : "slt",
#   "source_filename" : "source_filename",
    "speculatable" : "speculatable",
    "spFlags:" : "spFlags_colon",
    "spir_func" : "spir_func",
    "spir_kernel" : "spir_kernel",
    "splitDebugFilename:" : "splitDebugFilename_colon",
    "splitDebugInlining:" : "splitDebugInlining_colon",
    "srem" : "srem",
    "sret" : "sret",
    "sspreq" : "sspreq",
    "ssp" : "ssp",
    "sspstrong" : "sspstrong",
    "store" : "store",
    "strictfp" : "strictfp",
    "sub" : "sub",
    "swiftcc" : "swiftcc",
    "swifterror" : "swifterror",
    "swiftself" : "swiftself",
#   "switch" : "switch_kw",
    "syncscope" : "syncscope",
    "tag:" : "tag_colon",
    "tail" : "tail",
#   "target" : "target",
    "templateParams:" : "templateParams_colon",
    "thisAdjustment:" : "thisAdjustment_colon",
#   "thread_local" : "thread_local",
    "thrownTypes:" : "thrownTypes_colon",
    "token" : "token",
    "to" : "to",
#   "triple" : "triple",
    "true" : "true_kw",
    "trunc" : "trunc",
    "type:" : "type_colon",
    "types:" : "types_colon",
#   "type" : "type",
    "udiv" : "udiv",
    "ueq" : "ueq",
    "uge" : "uge",
    "ugt" : "ugt",
    "uitofp" : "uitofp",
    "ule" : "ule",
    "ult" : "ult",
    "umax" : "umax",
    "umin" : "umin",
    "undef" : "undef",
    "une" : "une",
    "unit:" : "unit_colon",
#   "unnamed_addr" : "unnamed_addr",
    "unordered" : "unordered",
    "uno" : "uno",
#   "unreachable" : "unreachable",
#   "unwind" : "unwind",
    "urem" : "urem",
#   "uselistorder_bb" : "uselistorder_bb",
#   "uselistorder" : "uselistorder",
    "uwtable" : "uwtable",
    "va_arg" : "va_arg",
    "value:" : "value_colon",
    "var:" : "var_colon",
    "variables:" : "variables_colon",
    "virtualIndex:" : "virtualIndex_colon",
    "virtuality:" : "virtuality_colon",
    "void" : "void_kw",
    "volatile" : "volatile_kw",
    "vtableHolder:" : "vtableHolder_colon",
#   "weak_odr" : "weak_odr",
    "weak" : "weak",
    "webkit_jscc" : "webkit_jscc",
    "win64cc" : "win64cc",
    "within" : "within",
    "writeonly" : "writeonly",
    "x86_64_sysvcc" : "x86_64_sysvcc",
    "x86_fastcallcc" : "x86_fastcallcc",
    "x86_fp80" : "x86_fp80",
    "x86_intrcc" : "x86_intrcc",
    "x86_mmx" : "x86_mmx",
    "x86_regcallcc" : "x86_regcallcc",
    "x86_stdcallcc" : "x86_stdcallcc",
    "x86_thiscallcc" : "x86_thiscallcc",
    "x86_vectorcallcc" : "x86_vectorcallcc",
    "xchg" : "xchg",
    "xor" : "xor",
    "zeroext" : "zeroext",
    "zeroinitializer" : "zeroinitializer",
    "zext" : "zext",

    "!DIBasicType" : "not_DIBasicType",
    "!DICompileUnit" : "not_DICompileUnit",
    "!DICompositeType" : "not_DICompositeType",
    "!DIDerivedType" : "not_DIDerivedType",
    "!DIEnumerator" : "not_DIEnumerator",
    "!DIExpression" : "not_DIExpression",
    "!DIFile" : "not_DIFile",
    "!DIGlobalVariable" : "not_DIGlobalVariable",
    "!DIGlobalVariableExpression" : "not_DIGlobalVariableExpression",
    "!DIImportedEntity" : "not_DIImportedEntity",
    "!DILexicalBlock" : "not_DILexicalBlock",
    "!DILexicalBlockFile" : "not_DILexicalBlockFile",
    "!DILocalVariable" : "not_DILocalVariable",
    "!DILocation" : "not_DILocation",
    "!DIMacro" : "not_DIMacro",
    "!DIMacroFile" : "not_DIMacroFile",
    "!DINamespace" : "not_DINamespace",
    "!DIObjCProperty" : "not_DIObjCProperty",
    "!DISubprogram" : "not_DISubprogram",
    "!DISubrange" : "not_DISubrange",
    "!DISubroutineType" : "not_DISubroutineType",
    "!DITemplateTypeParameter" : "not_DITemplateTypeParameter",
    "!DITemplateValueParameter" : "not_DITemplateValueParameter",
    "!DILabel" : "not_DILabel",

    "DISPFlagLocalToUnit" : "DISPFlagLocalToUnit",
    "DISPFlagDefinition" : "DISPFlagDefinition",

    }

# ============================================================
#
# These were in the grammar but with some productions and
# nonterminals removed (see parser comments) they are no
# longer used.
#
#    "configmacros:" : "configMacros_colon",
#    "expr:" : "expr_colon",
#    "header:" : "header_colon",
#    "includepath:" : "includePath_colon",
#    "isysroot:" : "isysroot_colon",
#    "operands:" : "operands_colon",
#    "var:" : "var_colon",
#
# ============================================================

tokens = [ 'attr_group_id',
           'checksum_kind',
#          'comdat_name',
#          'comment', 
           'decimals',
           'di_flag',
           'dwarf_tag', 'dwarf_att_encoding', 'dwarf_lang', 'dwarf_cc', 'dwarf_virtuality', 'dwarf_macinfo', 'dwarf_op',
           'float_hex_lit',
           'frac_lit',
           'global_ident',
           'int_type',
#          'label_ident',
           'local_ident',
           'metadata_id',
           'metadata_name',
           'name', 
           'quoted_string', 
           'sci_lit', 
         ]

# ============================================================
#
# Literals to pass through intact, a-la flex.
# A good list is at https://github.com/llir/grammar/blob/master/ll.tm
#
# ============================================================

literals = [ ',', '!', '(', ')', '[', ']', '{', '}', '*', '<', '=', '>', '|' ]

# ============================================================
#
# The specification from the web site (above) has things like
# "_name" instead of just "name", but I wasn't sure if PLY would
# take these, so I left off the underscores. 
#
# I used parens and "or" to mimick the web regular expressions, so 
# I have [A-Z]|[a-z] for ascii_letter, not [A-Za-z] and all are
# way over the top in terms of parens' so that they exactly match
# the web site.
#
# ============================================================
#
# ascii_letter_upper     ([A-Z])
# ascii_letter_lower     ([a-z])
# ascii_letter           (([A-Z])|([a-z]))
# letter                 (([A-Z])|([a-z])|([$\-\._]))
# escape_letter          (([A-Z])|([a-z])|([$\-\._])|([\\]))
# decimal_digit          ([0-9])
# hex_digit              (([0-9)|([A-F])|([a-f]))
# comment                ([;][^\r\n]*)
# whitespace             ([\t\r\n])
# name                   (([A-Z])|([a-z])|([$\-\._]))((([A-Z])|([a-z])|([$\-\._]))|([0-9]))*
# escape_name            (([A-Z])|([a-z])|([$\-\._])|([\\]))((([A-Z])|([a-z])|([$\-\._])|([\\]))|(0-9))*
# quoted_name            (["][^"]*["])       <--- the same token as
# quoted_string          (["][^"]*["])       <--- ???
# id                     ([0-9]+)            <--- the same token as
# decimals               ([0-9]+)            <--- ???
# label_ident            (((([A-Z])|([a-z])|([$\-\._]))|([0-9]))((([A-Z])|([a-z])|([$\-\._]))|([0-9]))*):
# int_type               (i[0-9]+)
#
# ============================================================
#
# These we will handle as special cases:
#
# global_ident           '@' name | '@' quoted_name | '@' id
# local_ident            '%' name | '%' quoted_name | '%' id
# attr_group_id          '#' decimals
# comdat_name            '$' name | '$' quoted_string
# metadata_name          '!' escape_name
# metadata_id            '!' decimals
#
# ============================================================
#
# And then there is ambiguity because certain tokens have
# more than one name? So in the grammar (at the tail end):
#
# string_lit    -> quoted_string
# int_lit       -> decimal_lit
# decimal_lit   -> '-' decimals | decimals
# float_lit     -> frac_lit | sci_lit | float_hex_lit
#
# And just to make matters worse, _id and _quoted_name are in
# the grammar spec but never referenced anywhere. So we omit:
#
# id            -> decimals
# quoted_name   -> quoted_string
#
# ============================================================

# ============================================================
# Dwarf items have priority over names as well. Some could
# be combined but I did not bother.
# ============================================================
def t_dwarf_tag(t):
    r'DW_TAG_([a-zA-Z0-9_])*'
    return t

def t_dwarf_att_encoding(t):
    r'DW_ATE_([a-zA-Z0-9_])*'
    return t

def t_di_flag(t):
    r'DIFlag([a-zA-Z0-9_])*'
    return t

def t_dwarf_lang(t):
    r'DW_LANG_([a-zA-Z0-9_])*'
    return t

def t_dwarf_cc(t):
    r'DW_CC_([a-zA-Z0-9_])*'
    return t

def t_checksum_kind(t):
    r'CSK_([a-zA-Z0-9_])*'
    return t

def t_dwarf_virtuality(t):
    r'DW_VIRTUALITY_([a-zA-Z0-9_])*'
    return t

def t_dwarf_macinfo(t):
    r'DW_MACINFO_([a-zA-Z0-9_])*'
    return t

def t_dwarf_op(t):
    r'DW_OP_([a-zA-Z0-9_])*'
    return t

# ============================================================
# Normally we'd toss the comments but eventually we will
# want to recreate an output file from the parse tree and
# we may as well include the comments in there as well...
#
# Well for now they cause a syntax error, so toss them.
# ============================================================
def t_comment(t):
    r';.*\n'
    pass
    # return t

# ============================================================
# float_lit     -> frac_lit | sci_lit | float_hex_lit
# Various floating point numbers.
# ============================================================
# Scientific notation. Needs to be before frac_lit.
def t_sci_lit(t):
    r'((\+[0-9]+\.[0-9]*)|(-[0-9]+\.[0-9]*)|([0-9]+\.[0-9]*))[eE]((\+[0-9]+)|(\-[0-9]+)|([0-9]+))'
    return t

# Plain old fractional
def t_frac_lit(t):
    r'(\+[0-9]+\.[0-9]*)|(\-[0-9]+\.[0-9]*)|([0-9]+\.[0-9]*)'
    return t

# Various kinds of hex constants.
def t_float_hex_lit(t):
    r'(0x[0-9A-Fa-f]+)|(0xK[0-9A-Fa-f]+)|(0xL[0-9A-Fa-f]+)|(0xM[0-9A-Fa-f]+)|(0xH[0-9A-Fa-f]+)'
    return t # float_lit -> hex constants of various varieties

# ============================================================
# label_ident
# This is also poorly done. Certain things "look like a label" and
# they "regex like a label" but they're not labels. These are
# the things like "name_colon" that are, in fact, keywords. Yuck.
# ============================================================
def t_label_ident(t):
    r'(((([A-Z])|([a-z])|([$\-\._]))|([0-9]))((([A-Z])|([a-z])|([$\-\._]))|([0-9]))*):'
    if ( reserved.get( t.value ) != None ):
        t.type = reserved.get( t.value )
    return t

# ============================================================
# decimals / id
# May really be a global_ident if it starts with '@'.
# May really be a local_ident if it starts with '%'.
# May really be a attr_group_id if it starts with '#'.
# May really be a metadata_id if it starts with '!'.
# ============================================================
def t_decimals(t):
    r'([@%#!\-])?([0-9]+)'
    if ( t.value[0:1] == '@' ):
        t.type = 'global_ident'
    elif ( t.value[0:1] == '%' ):
        t.type = 'local_ident'
    elif ( t.value[0:1] == '#' ):
        t.type = 'attr_group_id'
    elif ( t.value[0:1] == '!' ):
        t.type = 'metadata_id'
    # and if it starts with - it's just negative.
    return t

# ============================================================
# Need to have i32 before names are matched
# ============================================================
def t_int_type(t):
    r'(i[0-9]+)'
    return t

# ============================================================
# Need to have name before escape_name.
# May really be a global_ident if it starts with '@'.
# May really be a local_ident if it starts with '%'.
# May really be a comdat_name if it starts with '$'.
# ============================================================
def t_name(t):
    r'([@%$])?(([A-Z])|([a-z])|([$\-\._]))((([A-Z])|([a-z])|([$\-\._]))|([0-9]))*'
    if ( t.value[0:1] == '@' ):
        t.type = 'global_ident'
    elif ( t.value[0:1] == '%' ):
        t.type = 'local_ident'
    elif ( t.value[0:1] == '$' ):
        t.type = 'comdat_name'
    elif ( reserved.get( t.value ) != None ):
        t.type = reserved.get( t.value )
    return t

# ============================================================
# escape_name / metadata_name
# If it starts with '!' then it is a metadata_name.
# Otherwise if it is reserved then go with it.
# But the truth is that escape_name is never used
# anywhere other than for metadata_name, so I have
# eliminated plain escape_name from the scanner.
# def t_escape_name(t):
#     r'([!])?(([A-Z])|([a-z])|([$\-\._])|([\\]))((([A-Z])|([a-z])|([$\-\._])|([\\]))|(0-9))*'
#     if ( t.value[0:1] == '!' ):
#         t.type = 'metadata_name'
#     elif ( reserved.get( t.value ) != None ):
#         t.type = reserved.get( t.value )
#    return t
# ============================================================
def t_metadata_name(t):
    r'[!](([A-Z])|([a-z])|([$\-\._])|([\\]))((([A-Z])|([a-z])|([$\-\._])|([\\]))|(0-9))*'
    # There is some subtle diffrerence between what is a metadata_name versus
    # what is a not_DIExpression (for example). So check that they are not
    # keywords here as well.
    if ( reserved.get( t.value ) != None ):
        t.type = reserved.get( t.value )
    return t

# ============================================================
# quoted_string / quoted_name
# May really be a global_ident if it starts with '@'.
# May really be a local_ident if it starts with '%'.
# May really be a comdat_name if it starts with '$'.
# ============================================================
def t_quoted_string(t):
    r'([@%$])?(["][^"]*["])'
    if ( t.value[0:1] == '@' ):
        t.type = 'global_ident'
    elif ( t.value[0:1] == '%' ):
        t.type = 'local_ident'
    elif ( t.value[0:1] == '$' ):
        t.type = 'comdat_name'
    return t

# ============================================================
# Now that the tokens are all defined, combine in the keywords too.
# ============================================================
tokens = tokens + list( reserved.values() )

# ============================================================
# Ignore whitespace other than newlines.
# ============================================================
t_ignore = " \t\r"

# ============================================================
# For errors we may want the line number
# ============================================================
def t_newline(t):
    r'\n+'
    global line_number
    t.lexer.lineno += t.value.count("\n")
    line_number = t.lexer.lineno

# ============================================================
# Token for error handling
# ============================================================
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# ============================================================
#
# Tree node class - holds the node type and children.
#
# For each node we will maintain the children (of course) but also the
# parent. Any new child that is a string (these are the terminals)
# will be automatically converted to Node as they are added.
#
# ============================================================

_Node__serial_number = 0

class Node:

    ############################################################
    # Constructor.
    #
    # NOTE: The parameter "newkids" works fine for the guts of the parser,
    # where the sub-parse-tree is in that position. But do NOT do this:
    #    xyz = Node( 'TheNodeType', [ child1, child2, child3 ] )
    # You need to create it with empty children and then do:
    #    xyz = Node( 'TheNodeType', [] )
    #    xyz.children.append( child1 )
    # Etc.
    #
    ############################################################
    def __init__( self, nodetype, newkids ):
        global __serial_number
        self.serial = __serial_number
        __serial_number = __serial_number + 1
        self.title = ""
        self.nodetype = nodetype
        self.children = []
        self.parent = None
        self.was_terminal = False
        self.is_epsilon = False
        # line_number basically just doesn't work right.
        self.line = line_number
        # Go down the list of RHS elements and convert any
        # that are type "str" into type "Node".
        for x in range( 1, len( newkids[1:] ) + 1 ):
            if ( type( newkids[ x ] ) == str ):
                newkids[ x ] = Node( newkids[ x ], [] )
                newkids[ x ].was_terminal = True

            # Temporary debugging. Is this child a NoneType?
            if ( newkids[ x ] is None ):
                print( "I have the NoneType here and the LHS is " + nodetype + '\n' )
                print( "Other children:\n" )
                for x in range( 1, len( newkids[1:] ) + 1 ):
                    print( "    " + newkids[ x ].nodetype + '\n' )
                    
            # OK, they may have been converted from "str"
            # or maybe not, but now for each of these,
            # the parent is this node.
            newkids[ x ].parent = self
            self.children.append( newkids[ x ] )

    ############################################################
    # Dump to an ASCII file in "lispey" notation.  This was before I
    # converted token strings to also be tree nodes, so it handles
    # strings, but I didn't take it out.
    ############################################################
    def dump( self, depth=0 ):
        if ( depth > 0 ):
            for i in range(0,depth*4):
                print( ' ', end='', sep='' )
        print( '(', self.nodetype, sep='' )
        kids = len( self.children )
        if ( kids > 0 ):
            for x in self.children:
                if ( type( x ) is str ):
                    for i in range(0,depth*4):
                        print( ' ', end='', sep='' )
                    print( '"', x, '" ', sep='' )
                else:
                    x.dump( depth + 1 )
        for i in range(0,depth*4):
            print( ' ', end='', sep='' )
        print( ')' )

    ############################################################
    # Similar, but make a long lisp-ey string that can be compared later.
    ############################################################
    def tree_as_string( self ):
        pr = '(' + self.nodetype
        kids = len( self.children )
        if ( kids > 0 ):
            for x in self.children:
                pr = pr + x.tree_as_string()
        pr = pr + ')'
        return pr

    ############################################################
    # Dump out a "dot" file for the graphviz "dot" command.
    ############################################################
    def graph( self, filename, destroy = False ):
        # Don't destroy an existing file unless asked.
        if ( destroy ):
            file = None
        else:
            try:
                file = open( filename, "r" )
            except FileNotFoundError:
                file = None
        if ( file == None ):    
            file = open( filename, "w" )
            file.write( "digraph llvm_parse {\n" )
            self.__generate( file )
            file.write( "}\n" )
            file.close()
        else:
            print( "That dot and txt file exists - I am not overwriting it, please delete it first." )

    ############################################################
    # Helper function for "graph".
    ############################################################
    def __generate( self, file ):
        kids = len( self.children )
        if ( kids > 0 ):
            left = ''
            if ( self.title != "" ):
                # The title string might have double quotes, confusing "dot".
                left = self.title.replace( '"', '\\"' ) + '\\n'
            left = '"' + left + self.nodetype + '\\n(Node ' + str(self.serial) + ')"'
            # "dot" gets confused with '%' in the string. Maybe everywhere,
            # but certainly if the label string starts with it. For instance
            # if the title is "%4\n..." you get a node in the graph with a 
            # label like %1759 or some seemingly random number. 
            left = left.replace( '%', '\\%' )
            for x in self.children:
                if ( x.was_terminal ):
                    right = '"' + x.nodetype.replace('"', '\\"' ) + '\\n(Node ' + str(x.serial) + ')\\n(terminal)"'
                else:
                    right = '"' + x.nodetype + '\\n(Node ' + str(x.serial) + ')"'
                right = right.replace( '%', '\\%' )
                file.write( '\t' + left + ' -> ' + right + '\n' )
                # Just to be efficient here. Terminals have no kids.
                if ( not x.was_terminal ):
                    x.__generate( file )

    ############################################################
    # This is used by others (not in this file).
    # It's just a DFS for a particular node in the tree.
    # I was not testing terminals but figured "why not".
    ############################################################
    def locate_tree_node( self, look_for ):
        # print( "Compare " + self.nodetype + " to " + look_for )
        if ( self.nodetype == look_for ):
            return self
        else:
            for x in self.children:
                there = x.locate_tree_node( look_for )
                if ( there != None ):
                    return there

    ############################################################
    # This is used by others (not in this file).
    # Scan "across" the children of a node, looking for something, but
    # do not go deeper than the immediate children. This is useful to
    # outsiders that might want to know "is there a such-and-such"
    # directly under this?
    ############################################################
    def locate_in_immediate_children( self, look_for ):
        for x in self.children:
            if ( x.nodetype == look_for ):
                return x
        return None

    ############################################################
    # Many times there is a long chain of nodes that ends in one
    # thing. For example, Type -> FirstClassType -> ConcreteType ->
    # IntType -> i32. If we know this is the case just follow all the
    # way to the end and return whatever is there.
    ############################################################
    def all_the_way_down( self ):
        here = self.root
        while ( not here.was_terminal ):
            here = here.children[ 0 ]
        return here.nodetype
    
# ============================================================
#
# Parser starts here. 
#
# Each production has "# Next" in front of it so that if we need to do
# something to ALL of them we can do an emacs macro and search for the
# string so we know where the next one starts. I hope. But - serch for
# the next production and then "back up" one line, becuse some
# productions have additional comments at the top.
#
# Here we are concerned only with parsing a single LLVM instruction,
# so the grammar is significantly cut down to have a start symbol as
# "instruction".
#
# ============================================================

# Note: Moved CmpXchgInst from Instruction to ValueInstruction
# Note: Moved AtomicRMWInst from Instruction to ValueInstruction
# Next
def p_Instruction(t):
    '''Instruction : StoreInst
    | FenceInst
    | LocalIdent '=' ValueInstruction
    | ValueInstruction
    '''
    t[ 0 ] = Node( 'Instruction', t )

# Next
def p_ValueInstruction(t):
    '''ValueInstruction : AddInst
    | FAddInst
    | SubInst
    | FSubInst
    | MulInst
    | FMulInst
    | UDivInst
    | SDivInst
    | FDivInst
    | URemInst
    | SRemInst
    | FRemInst
    | ShlInst
    | LShrInst
    | AShrInst
    | AndInst
    | OrInst
    | XorInst
    | ExtractElementInst
    | InsertElementInst
    | ShuffleVectorInst
    | ExtractValueInst
    | InsertValueInst
    | AllocaInst
    | LoadInst
    | GetElementPtrInst
    | TruncInst
    | ZExtInst
    | SExtInst
    | FPTruncInst
    | FPExtInst
    | FPToUIInst
    | FPToSIInst
    | UIToFPInst
    | SIToFPInst
    | PtrToIntInst
    | IntToPtrInst
    | BitCastInst
    | AddrSpaceCastInst
    | ICmpInst
    | FCmpInst
    | PhiInst
    | SelectInst
    | CallInst
    | VAArgInst
    | LandingPadInst
    | CatchPadInst
    | CleanupPadInst
    | CmpXchgInst
    | AtomicRMWInst
    '''
    t[ 0 ] = Node( 'ValueInstruction', t )

# Next
def p_AddInst(t):
    '''AddInst : add OverflowFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'AddInst', t )

# Next
def p_FAddInst(t):
    '''FAddInst : fadd FastMathFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FAddInst', t )

# Next
def p_SubInst(t):
    '''SubInst : sub OverflowFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'SubInst', t )

# Next
def p_FSubInst(t):
    '''FSubInst : fsub FastMathFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FSubInst', t )

# Next
def p_MulInst(t):
    '''MulInst : mul OverflowFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'MulInst', t )

# Next
def p_FMulInst(t):
    '''FMulInst : fmul FastMathFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FMulInst', t )

# Next
def p_UDivInst(t):
    '''UDivInst : udiv OptExact Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'UDivInst', t )

# Next
def p_SDivInst(t):
    '''SDivInst : sdiv OptExact Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'SDivInst', t )

# Next
def p_FDivInst(t):
    '''FDivInst : fdiv FastMathFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FDivInst', t )

# Next
def p_URemInst(t):
    '''URemInst : urem Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'URemInst', t )

# Next
def p_SRemInst(t):
    '''SRemInst : srem Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'SRemInst', t )

# Next
def p_FRemInst(t):
    '''FRemInst : frem FastMathFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FRemInst', t )

# Next
def p_ShlInst(t):
    '''ShlInst : shl OverflowFlags Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'ShlInst', t )

# Next
def p_LShrInst(t):
    '''LShrInst : lshr OptExact Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'LShrInst', t )

# Next
def p_AShrInst(t):
    '''AShrInst : ashr OptExact Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'AShrInst', t )

# Next
def p_AndInst(t):
    '''AndInst : and_kw Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'AndInst', t )

# Next
def p_OrInst(t):
    '''OrInst : or_kw Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'OrInst', t )

# Next
def p_XorInst(t):
    '''XorInst : xor Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'XorInst', t )

# Next
def p_ExtractElementInst(t):
    '''ExtractElementInst : extractelement Type Value ',' Type Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'ExtractElementInst', t )

# Next
def p_InsertElementInst(t):
    '''InsertElementInst : insertelement Type Value ',' Type Value ',' Type Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'InsertElementInst', t )

# Next
def p_ShuffleVectorInst(t):
    '''ShuffleVectorInst : shufflevector Type Value ',' Type Value ',' Type Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'ShuffleVectorInst', t )

# Next
def p_ExtractValueInst(t):
    '''ExtractValueInst : extractvalue Type Value ',' IndexList OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'ExtractValueInst', t )

# Next
def p_InsertValueInst(t):
    '''InsertValueInst : insertvalue Type Value ',' Type Value ',' IndexList OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'InsertValueInst', t )

# Next
def p_AllocaInst(t):
    '''AllocaInst : alloca OptInAlloca OptSwiftError Type OptCommaSepMetadataAttachmentList
    | alloca OptInAlloca OptSwiftError Type ',' Alignment OptCommaSepMetadataAttachmentList
    | alloca OptInAlloca OptSwiftError Type ',' Type Value OptCommaSepMetadataAttachmentList
    | alloca OptInAlloca OptSwiftError Type ',' Type Value ',' Alignment OptCommaSepMetadataAttachmentList
    | alloca OptInAlloca OptSwiftError Type ',' AddrSpace OptCommaSepMetadataAttachmentList
    | alloca OptInAlloca OptSwiftError Type ',' Alignment ',' AddrSpace OptCommaSepMetadataAttachmentList
    | alloca OptInAlloca OptSwiftError Type ',' Type Value ',' AddrSpace OptCommaSepMetadataAttachmentList
    | alloca OptInAlloca OptSwiftError Type ',' Type Value ',' Alignment ',' AddrSpace OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'AllocaInst', t )

# Next
def p_OptInAlloca(t):
    '''OptInAlloca : empty
    | inalloca
    '''
    t[ 0 ] = Node( 'OptInAlloca', t )

# Next
def p_OptSwiftError(t):
    '''OptSwiftError : empty
    | swifterror
    '''
    t[ 0 ] = Node( 'OptSwiftError', t )

# Next
def p_LoadInst(t):
    '''LoadInst : load OptVolatile Type ',' Type Value OptCommaSepMetadataAttachmentList
    | load OptVolatile Type ',' Type Value ',' Alignment OptCommaSepMetadataAttachmentList
    | load atomic OptVolatile Type ',' Type Value OptSyncScope AtomicOrdering OptCommaSepMetadataAttachmentList
    | load atomic OptVolatile Type ',' Type Value OptSyncScope AtomicOrdering ',' Alignment OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'LoadInst', t )

# Next
def p_StoreInst(t):
    '''StoreInst : store OptVolatile Type Value ',' Type Value OptCommaSepMetadataAttachmentList
    | store OptVolatile Type Value ',' Type Value ',' Alignment OptCommaSepMetadataAttachmentList
    | store atomic OptVolatile Type Value ',' Type Value OptSyncScope AtomicOrdering OptCommaSepMetadataAttachmentList
    | store atomic OptVolatile Type Value ',' Type Value OptSyncScope AtomicOrdering ',' Alignment OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'StoreInst', t )

# Next
def p_FenceInst(t):
    '''FenceInst : fence OptSyncScope AtomicOrdering OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FenceInst', t )

# Next
def p_CmpXchgInst(t):
    '''CmpXchgInst : cmpxchg OptWeak OptVolatile Type Value ',' Type Value ',' Type Value OptSyncScope AtomicOrdering AtomicOrdering OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'CmpXchgInst', t )

# Next
def p_OptWeak(t):
    '''OptWeak : empty
    | weak
    '''
    t[ 0 ] = Node( 'OptWeak', t )

# Next
def p_AtomicRMWInst(t):
    '''AtomicRMWInst : atomicrmw OptVolatile BinOp Type Value ',' Type Value OptSyncScope AtomicOrdering OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'AtomicRMWInst', t )

############################################################

# Next
def p_GlobalIdent(t):
    '''GlobalIdent : global_ident
    '''
    t[ 0 ] = Node( 'GlobalIdent', t )

# Next
def p_LocalIdent(t):
    '''LocalIdent : local_ident
    '''
    t[ 0 ] = Node( 'LocalIdent', t )

# Next
def p_AttrGroupID(t):
    '''AttrGroupID : attr_group_id
    '''
    t[ 0 ] = Node( 'AttrGroupID', t )

# Next
def p_MetadataID(t):
    '''MetadataID : metadata_id
    '''
    t[ 0 ] = Node( 'MetadataID', t )

# Next
def p_Type(t):
    '''Type : VoidType
    | FuncType
    | FirstClassType
    '''
    t[ 0 ] = Node( 'Type', t )

# Next
def p_FirstClassType(t):
    '''FirstClassType : ConcreteType
    | MetadataType
    '''
    t[ 0 ] = Node( 'FirstClassType', t )

# Next
def p_ConcreteType(t):
    '''ConcreteType : IntType
    | FloatType
    | PointerType
    | VectorType
    | LabelType
    | ArrayType
    | StructType
    | NamedType
    | MMXType
    | TokenType
    '''
    t[ 0 ] = Node( 'ConcreteType', t )

# Next
def p_VoidType(t):
    '''VoidType : void_kw
    '''
    t[ 0 ] = Node( 'VoidType', t )

# Next
def p_FuncType(t):
    '''FuncType : Type '(' Params ')'
    '''
    t[ 0 ] = Node( 'FuncType', t )

# Next
def p_IntType(t):
    '''IntType : int_type
    '''
    t[ 0 ] = Node( 'IntType', t )

# Next
def p_FloatType(t):
    '''FloatType : FloatKind
    '''
    t[ 0 ] = Node( 'FloatType', t )

# Next
def p_FloatKind(t):
    '''FloatKind : half
    | float_kw
    | double_kw
    | x86_fp80
    | fp128
    | ppc_fp128
    '''
    t[ 0 ] = Node( 'FloatKind', t )

# Next
def p_MMXType(t):
    '''MMXType : x86_mmx
    '''
    t[ 0 ] = Node( 'MMXType', t )

# Note: LLVM 15 suddenly allows things like this:
#       store i32 %0, ptr %3, align 4
# Where "ptr" is just a generic word. I don't know
# if this will ever have an OptAddrSpace or not.
# Next
def p_PointerType(t):
    '''PointerType : Type OptAddrSpace '*'
    | ptr 
    '''
    t[ 0 ] = Node( 'PointerType', t )

# Next
def p_OptAddrSpace(t):
    '''OptAddrSpace : empty
    | AddrSpace
    '''
    t[ 0 ] = Node( 'OptAddrSpace', t )

# Next
def p_AddrSpace(t):
    '''AddrSpace : addrspace '(' int_lit ')'
    '''
    t[ 0 ] = Node( 'AddrSpace', t )

# Next
# The same issue is here that is at ArrayType.
# We don't get a literal 'x' we get a token
# of type 'name'.
#
#    '''VectorType : '<' int_lit 'x' Type '>'
#    '''
def p_VectorType(t):
    '''VectorType : '<' int_lit name Type '>'
    '''
    if ( t[ 3 ] != "x" ):
        print( "Parsing VectorType but the name is not 'x'?" )
        raise SyntaxError
    t[ 0 ] = Node( 'VectorType', t )

# Next
def p_LabelType(t):
    '''LabelType : label
    '''
    t[ 0 ] = Node( 'LabelType', t )

# Next
def p_TokenType(t):
    '''TokenType : token
    '''
    t[ 0 ] = Node( 'TokenType', t )

# Next
def p_MetadataType(t):
    '''MetadataType : metadata
    '''
    t[ 0 ] = Node( 'MetadataType', t )

# Next
# Ambiguity correction here. The original rule is:
#     ArrayType -> '[' int_lit 'x' Type ']'
# but 'x' is a token of type "name". If we arrange
# for 'x' as a literal, then variables named "x" will
# break. So to check this I've changed the rule to:
#     ArrayType -> '[' int_lit name Type ']'
# and we'll throw a syntax error if it is not "x".
#
#    '''ArrayType : '[' int_lit 'x' Type ']'
#    '''
def p_ArrayType(t):
    '''ArrayType : '[' int_lit name Type ']'
    '''
    # print( 'here we are and t[3].value is', t[3] )
    if ( t[ 3 ] != "x" ):
        print( "Parsing ArrayType but the name is not 'x'?" )
        raise SyntaxError
    t[ 0 ] = Node( 'ArrayType', t )

# Next
def p_StructType(t):
    '''StructType : '{' '}'
    | '{' TypeList '}'
    | '<' '{' '}' '>'
    | '<' '{' TypeList '}' '>'
    '''
    t[ 0 ] = Node( 'StructType', t )

# Next
def p_TypeList(t):
    '''TypeList : Type
    | TypeList ',' Type
    '''
    t[ 0 ] = Node( 'TypeList', t )

# Next
def p_NamedType(t):
    '''NamedType : LocalIdent
    '''
    t[ 0 ] = Node( 'NamedType', t )

# Next
def p_Value(t):
    '''Value : Constant
    | LocalIdent
    | InlineAsm
    '''
    t[ 0 ] = Node( 'Value', t )

# Next
def p_InlineAsm(t):
    '''InlineAsm : asm_kw OptSideEffect OptAlignStack OptIntelDialect StringLit ',' StringLit
    '''
    t[ 0 ] = Node( 'InlineAsm', t )

# Next
def p_OptSideEffect(t):
    '''OptSideEffect : empty
    | sideeffect
    '''
    t[ 0 ] = Node( 'OptSideEffect', t )

# Next
def p_OptAlignStack(t):
    '''OptAlignStack : empty
    | alignstack
    '''
    t[ 0 ] = Node( 'OptAlignStack', t )

# Next
def p_OptIntelDialect(t):
    '''OptIntelDialect : empty
    | inteldialect
    '''
    t[ 0 ] = Node( 'OptIntelDialect', t )

# Next
def p_Constant(t):
    '''Constant : BoolConst
    | IntConst
    | FloatConst
    | NullConst
    | NoneConst
    | StructConst
    | ArrayConst
    | CharArrayConst
    | VectorConst
    | ZeroInitializerConst
    | GlobalIdent
    | UndefConst
    | BlockAddressConst
    | ConstantExpr
    '''
    t[ 0 ] = Node( 'Constant', t )

# Next
def p_BoolConst(t):
    '''BoolConst : BoolLit
    '''
    t[ 0 ] = Node( 'BoolConst', t )

# Next
def p_BoolLit(t):
    '''BoolLit : true_kw
    | false_kw
    '''
    t[ 0 ] = Node( 'BoolLit', t )

# Next
def p_IntConst(t):
    '''IntConst : int_lit
    '''
    t[ 0 ] = Node( 'IntConst', t )

# Next
def p_IntLit(t):
    '''IntLit : int_lit
    '''
    t[ 0 ] = Node( 'IntLit', t )

# Next
def p_FloatConst(t):
    '''FloatConst : float_lit
    '''
    t[ 0 ] = Node( 'FloatConst', t )

# Next
def p_NullConst(t):
    '''NullConst : null
    '''
    t[ 0 ] = Node( 'NullConst', t )

# Next
def p_NoneConst(t):
    '''NoneConst : none
    '''
    t[ 0 ] = Node( 'NoneConst', t )

# Next
def p_StructConst(t):
    '''StructConst : '{' '}'
    | '{' TypeConstList '}'
    | '<' '{' '}' '>'
    | '<' '{' TypeConstList '}' '>'
    '''
    t[ 0 ] = Node( 'StructConst', t )

# Next
def p_ArrayConst(t):
    '''ArrayConst : '[' TypeConsts ']'
    '''
    t[ 0 ] = Node( 'ArrayConst', t )

# Next
# Same problem here as ArrayType. They expect
# a literal "c" here when this will scan as "name".
#
#     '''CharArrayConst : 'c' StringLit
#     '''
def p_CharArrayConst(t):
    '''CharArrayConst : name StringLit
    '''
    if ( t[ 1 ] != "c" ):
        print( "Parsing CharArrayConst but the name is not 'c' ???" )
        raise SyntaxError
    t[ 0 ] = Node( 'CharArrayConst', t )

# Next
def p_StringLit(t):
    '''StringLit : string_lit
    '''
    t[ 0 ] = Node( 'StringLit', t )

# Next
def p_VectorConst(t):
    '''VectorConst : '<' TypeConsts '>'
    '''
    t[ 0 ] = Node( 'VectorConst', t )

# Next
def p_ZeroInitializerConst(t):
    '''ZeroInitializerConst : zeroinitializer
    '''
    t[ 0 ] = Node( 'ZeroInitializerConst', t )

# Next
def p_UndefConst(t):
    '''UndefConst : undef
    '''
    t[ 0 ] = Node( 'UndefConst', t )

# Next
def p_BlockAddressConst(t):
    '''BlockAddressConst : blockaddress '(' GlobalIdent ',' LocalIdent ')'
    '''
    t[ 0 ] = Node( 'BlockAddressConst', t )

# Next
def p_ConstantExpr(t):
    '''ConstantExpr : AddExpr
    | FAddExpr
    | SubExpr
    | FSubExpr
    | MulExpr
    | FMulExpr
    | UDivExpr
    | SDivExpr
    | FDivExpr
    | URemExpr
    | SRemExpr
    | FRemExpr
    | ShlExpr
    | LShrExpr
    | AShrExpr
    | AndExpr
    | OrExpr
    | XorExpr
    | ExtractElementExpr
    | InsertElementExpr
    | ShuffleVectorExpr
    | ExtractValueExpr
    | InsertValueExpr
    | GetElementPtrExpr
    | TruncExpr
    | ZExtExpr
    | SExtExpr
    | FPTruncExpr
    | FPExtExpr
    | FPToUIExpr
    | FPToSIExpr
    | UIToFPExpr
    | SIToFPExpr
    | PtrToIntExpr
    | IntToPtrExpr
    | BitCastExpr
    | AddrSpaceCastExpr
    | ICmpExpr
    | FCmpExpr
    | SelectExpr
    '''
    t[ 0 ] = Node( 'ConstantExpr', t )

# Next
def p_AddExpr(t):
    '''AddExpr : add OverflowFlags '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'AddExpr', t )

# Next
def p_FAddExpr(t):
    '''FAddExpr : fadd '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'FAddExpr', t )

# Next
def p_SubExpr(t):
    '''SubExpr : sub OverflowFlags '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'SubExpr', t )

# Next
def p_FSubExpr(t):
    '''FSubExpr : fsub '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'FSubExpr', t )

# Next
def p_MulExpr(t):
    '''MulExpr : mul OverflowFlags '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'MulExpr', t )

# Next
def p_FMulExpr(t):
    '''FMulExpr : fmul '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'FMulExpr', t )

# Next
def p_UDivExpr(t):
    '''UDivExpr : udiv OptExact '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'UDivExpr', t )

# Next
def p_SDivExpr(t):
    '''SDivExpr : sdiv OptExact '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'SDivExpr', t )

# Next
def p_FDivExpr(t):
    '''FDivExpr : fdiv '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'FDivExpr', t )

# Next
def p_URemExpr(t):
    '''URemExpr : urem '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'URemExpr', t )

# Next
def p_SRemExpr(t):
    '''SRemExpr : srem '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'SRemExpr', t )

# Next
def p_FRemExpr(t):
    '''FRemExpr : frem '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'FRemExpr', t )

# Next
def p_ShlExpr(t):
    '''ShlExpr : shl OverflowFlags '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'ShlExpr', t )

# Next
def p_LShrExpr(t):
    '''LShrExpr : lshr OptExact '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'LShrExpr', t )

# Next
def p_AShrExpr(t):
    '''AShrExpr : ashr OptExact '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'AShrExpr', t )

# Next
def p_AndExpr(t):
    '''AndExpr : and_kw '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'AndExpr', t )

# Next
def p_OrExpr(t):
    '''OrExpr : or_kw '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'OrExpr', t )

# Next
def p_XorExpr(t):
    '''XorExpr : xor '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'XorExpr', t )

# Next
def p_ExtractElementExpr(t):
    '''ExtractElementExpr : extractelement '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'ExtractElementExpr', t )

# Next
def p_InsertElementExpr(t):
    '''InsertElementExpr : insertelement '(' Type Constant ',' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'InsertElementExpr', t )

# Next
def p_ShuffleVectorExpr(t):
    '''ShuffleVectorExpr : shufflevector '(' Type Constant ',' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'ShuffleVectorExpr', t )

# Next
def p_ExtractValueExpr(t):
    '''ExtractValueExpr : extractvalue '(' Type Constant Indices ')'
    '''
    t[ 0 ] = Node( 'ExtractValueExpr', t )

# Next
def p_InsertValueExpr(t):
    '''InsertValueExpr : insertvalue '(' Type Constant ',' Type Constant Indices ')'
    '''
    t[ 0 ] = Node( 'InsertValueExpr', t )

# Next
def p_GetElementPtrExpr(t):
    '''GetElementPtrExpr : getelementptr OptInBounds '(' Type ',' Type Constant ',' GEPConstIndices ')'
    '''
    t[ 0 ] = Node( 'GetElementPtrExpr', t )

# Next
def p_GEPConstIndices(t):
    '''GEPConstIndices : empty
    | GEPConstIndexList
    '''
    t[ 0 ] = Node( 'GEPConstIndices', t )

# Next
def p_GEPConstIndexList(t):
    '''GEPConstIndexList : GEPConstIndex
    | GEPConstIndexList ',' GEPConstIndex
    '''
    t[ 0 ] = Node( 'GEPConstIndexList', t )

# Next
def p_GEPConstIndex(t):
    '''GEPConstIndex : OptInrange Type Constant
    '''
    t[ 0 ] = Node( 'GEPConstIndex', t )

# Next
def p_OptInrange(t):
    '''OptInrange : empty
    | inrange
    '''
    t[ 0 ] = Node( 'OptInrange', t )

# Next
def p_TruncExpr(t):
    '''TruncExpr : trunc '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'TruncExpr', t )

# Next
def p_ZExtExpr(t):
    '''ZExtExpr : zext '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'ZExtExpr', t )

# Next
def p_SExtExpr(t):
    '''SExtExpr : sext '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'SExtExpr', t )

# Next
def p_FPTruncExpr(t):
    '''FPTruncExpr : fptrunc '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'FPTruncExpr', t )

# Next
def p_FPExtExpr(t):
    '''FPExtExpr : fpext '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'FPExtExpr', t )

# Next
def p_FPToUIExpr(t):
    '''FPToUIExpr : fptoui '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'FPToUIExpr', t )

# Next
def p_FPToSIExpr(t):
    '''FPToSIExpr : fptosi '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'FPToSIExpr', t )

# Next
def p_UIToFPExpr(t):
    '''UIToFPExpr : uitofp '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'UIToFPExpr', t )

# Next
def p_SIToFPExpr(t):
    '''SIToFPExpr : sitofp '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'SIToFPExpr', t )

# Next
def p_PtrToIntExpr(t):
    '''PtrToIntExpr : ptrtoint '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'PtrToIntExpr', t )

# Next
def p_IntToPtrExpr(t):
    '''IntToPtrExpr : inttoptr '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'IntToPtrExpr', t )

# Next
def p_BitCastExpr(t):
    '''BitCastExpr : bitcast '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'BitCastExpr', t )

# Next
def p_AddrSpaceCastExpr(t):
    '''AddrSpaceCastExpr : addrspacecast '(' Type Constant to Type ')'
    '''
    t[ 0 ] = Node( 'AddrSpaceCastExpr', t )

# Next
def p_ICmpExpr(t):
    '''ICmpExpr : icmp IPred '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'ICmpExpr', t )

# Next
def p_FCmpExpr(t):
    '''FCmpExpr : fcmp FPred '(' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'FCmpExpr', t )

# Next
def p_SelectExpr(t):
    '''SelectExpr : select '(' Type Constant ',' Type Constant ',' Type Constant ')'
    '''
    t[ 0 ] = Node( 'SelectExpr', t )

# Next
def p_BinOp(t):
    '''BinOp : add
    | and_kw
    | max
    | min
    | nand
    | or_kw
    | sub
    | umax
    | umin
    | xchg
    | xor
    '''
    t[ 0 ] = Node( 'BinOp', t )

# Next
def p_GetElementPtrInst(t):
    '''GetElementPtrInst : getelementptr OptInBounds Type ',' Type Value OptCommaSepMetadataAttachmentList
    | getelementptr OptInBounds Type ',' Type Value ',' CommaSepTypeValueList OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'GetElementPtrInst', t )

# Next
def p_TruncInst(t):
    '''TruncInst : trunc Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'TruncInst', t )

# Next
def p_ZExtInst(t):
    '''ZExtInst : zext Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'ZExtInst', t )

# Next
def p_SExtInst(t):
    '''SExtInst : sext Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'SExtInst', t )

# Next
def p_FPTruncInst(t):
    '''FPTruncInst : fptrunc Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FPTruncInst', t )

# Next
def p_FPExtInst(t):
    '''FPExtInst : fpext Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FPExtInst', t )

# Next
def p_FPToUIInst(t):
    '''FPToUIInst : fptoui Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FPToUIInst', t )

# Next
def p_FPToSIInst(t):
    '''FPToSIInst : fptosi Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FPToSIInst', t )

# Next
def p_UIToFPInst(t):
    '''UIToFPInst : uitofp Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'UIToFPInst', t )

# Next
def p_SIToFPInst(t):
    '''SIToFPInst : sitofp Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'SIToFPInst', t )

# Next
def p_PtrToIntInst(t):
    '''PtrToIntInst : ptrtoint Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'PtrToIntInst', t )

# Next
def p_IntToPtrInst(t):
    '''IntToPtrInst : inttoptr Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'IntToPtrInst', t )

# Next
def p_BitCastInst(t):
    '''BitCastInst : bitcast Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'BitCastInst', t )

# Next
def p_AddrSpaceCastInst(t):
    '''AddrSpaceCastInst : addrspacecast Type Value to Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'AddrSpaceCastInst', t )

# Next
def p_ICmpInst(t):
    '''ICmpInst : icmp IPred Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'ICmpInst', t )

# Next
def p_FCmpInst(t):
    '''FCmpInst : fcmp FastMathFlags FPred Type Value ',' Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'FCmpInst', t )

# Next
def p_PhiInst(t):
    '''PhiInst : phi Type IncList OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'PhiInst', t )

# Next
def p_IncList(t):
    '''IncList : Inc
    | IncList ',' Inc
    '''
    t[ 0 ] = Node( 'IncList', t )

# Next
def p_Inc(t):
    '''Inc : '[' Value ',' LocalIdent ']'
    '''
    t[ 0 ] = Node( 'Inc', t )

# Next

def p_SelectInst(t):
    ''' SelectInst : select Type Value ',' Type Value ',' Type Value OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( '_SelectInst', t )

# Next
def p_CallInst(t):
    '''CallInst : OptTail call FastMathFlags OptCallingConv ReturnAttrs Type Value '(' Args ')' FuncAttrs OperandBundles OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'CallInst', t )

# Next
def p_OptTail(t):
    '''OptTail : empty
    | musttail
    | notail
    | tail
    '''
    t[ 0 ] = Node( 'OptTail', t )

# Next
def p_VAArgInst(t):
    '''VAArgInst : va_arg Type Value ',' Type OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'VAArgInst', t )

# Next
def p_OptCommaSepMetadataAttachmentList(t):
    '''OptCommaSepMetadataAttachmentList : empty
    | ',' CommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'OptCommaSepMetadataAttachmentList', t )

# Next
def p_CommaSepMetadataAttachmentList(t):
    '''CommaSepMetadataAttachmentList : MetadataAttachment
    | CommaSepMetadataAttachmentList ',' MetadataAttachment
    '''
    t[ 0 ] = Node( 'CommaSepMetadataAttachmentList', t )

# Next
def p_MetadataAttachment(t):
    '''MetadataAttachment : MetadataName MDNode
    '''
    t[ 0 ] = Node( 'MetadataAttachment', t )

# Next
def p_MetadataName(t):
    '''MetadataName : metadata_name
    '''
    t[ 0 ] = Node( 'MetadataName', t )

# Next
def p_MDNode(t):
    '''MDNode : MDTuple
    | MetadataID
    | SpecializedMDNode
    '''
    t[ 0 ] = Node( 'MDNode', t )

# Next
def p_MDTuple(t):
    '''MDTuple : '!' MDFields
    '''
    t[ 0 ] = Node( 'MDTuple', t )

# Next
def p_LandingPadInst(t):
    '''LandingPadInst : landingpad Type OptCleanup Clauses OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'LandingPadInst', t )

# Next
def p_OptCleanup(t):
    '''OptCleanup : empty
    | cleanup
    '''
    t[ 0 ] = Node( 'OptCleanup', t )

# Next
def p_Clauses(t):
    '''Clauses : empty
    | ClauseList
    '''
    t[ 0 ] = Node( 'Clauses', t )

# Next
def p_ClauseList(t):
    '''ClauseList : Clause
    | ClauseList Clause
    '''
    t[ 0 ] = Node( 'ClauseList', t )

# Next
def p_Clause(t):
    '''Clause : catch Type Value
    | filter Type ArrayConst
    '''
    t[ 0 ] = Node( 'Clause', t )

# Next
def p_CatchPadInst(t):
    '''CatchPadInst : catchpad within LocalIdent '[' ExceptionArgs ']' OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'CatchPadInst', t )

# Next
def p_CleanupPadInst(t):
    '''CleanupPadInst : cleanuppad within ExceptionScope '[' ExceptionArgs ']' OptCommaSepMetadataAttachmentList
    '''
    t[ 0 ] = Node( 'CleanupPadInst', t )

# Next
def p_MDFields(t):
    '''MDFields : '{' '}'
    | '{' MDFieldList '}'
    '''
    t[ 0 ] = Node( 'MDFields', t )

# Next
def p_MDFieldList(t):
    '''MDFieldList : MDField
    | MDFieldList ',' MDField
    '''
    t[ 0 ] = Node( 'MDFieldList', t )

# Next
def p_MDField(t):
    '''MDField : null
    | Metadata
    '''
    t[ 0 ] = Node( 'MDField', t )

# Next
def p_Metadata(t):
    '''Metadata : Type Value
    | MDString
    | MDTuple
    | MetadataID
    | SpecializedMDNode
    '''
    t[ 0 ] = Node( 'Metadata', t )

# Next
def p_MDString(t):
    '''MDString : '!' StringLit
    '''
    t[ 0 ] = Node( 'MDString', t )

# Next
# The grammar from the internet is missing DILabel. It is
# in the file "LLParser.cpp" in the LLVM source. Their example:
#    ::= !DILabel(scope: !0, name: "foo", file: !1, line: 7) 
# So there is an additional NT here for DILabel and I added the
# rules immediately following this NT.
def p_SpecializedMDNode(t):
    '''SpecializedMDNode : DICompileUnit
    | DIFile
    | DIBasicType
    | DISubroutineType
    | DIDerivedType
    | DICompositeType
    | DISubrange
    | DIEnumerator
    | DITemplateTypeParameter
    | DITemplateValueParameter
    | DINamespace
    | DIGlobalVariable
    | DISubprogram
    | DILexicalBlock
    | DILexicalBlockFile
    | DILocation
    | DILocalVariable
    | DIExpression
    | DIGlobalVariableExpression
    | DIObjCProperty
    | DIImportedEntity
    | DIMacro
    | DIMacroFile
    | DILabel
    '''
    # DIGlobalVariableExpression // not in spec as of 2018-02-21
    t[ 0 ] = Node( 'SpecializedMDNode', t )

# Next
# Added to the grammar see the rule directly before this - Bill
def p_DILabel(t):
    '''DILabel : not_DILabel '(' ScopeField ',' NameField ',' FileField ',' LineField ')'
    '''
    t[ 0 ] = Node( 'DILabel', t )

# Next
def p_DICompileUnit(t):
    '''DICompileUnit : not_DICompileUnit '(' DICompileUnitFields ')'
    '''
    t[ 0 ] = Node( 'DICompileUnit', t )

# Next
def p_DICompileUnitFields(t):
    '''DICompileUnitFields : empty
    | DICompileUnitFieldList
    '''
    t[ 0 ] = Node( 'DICompileUnitFields', t )

# Next
def p_DICompileUnitFieldList(t):
    '''DICompileUnitFieldList : DICompileUnitField
    | DICompileUnitFieldList ',' DICompileUnitField
    '''
    t[ 0 ] = Node( 'DICompileUnitFieldList', t )

# Next
# No clue what it is, but actual LLVM contains a token with
# "nameTableKind:" so it is added here last. I don't know the
# type of the field but a popular string to see is "None" so
# we will just anticipate a "name" token for this.
def p_DICompileUnitField(t):
    '''DICompileUnitField : language_colon DwarfLang
    | FileField
    | producer_colon StringLit
    | IsOptimizedField
    | flags_colon StringLit
    | runtimeVersion_colon IntLit
    | splitDebugFilename_colon StringLit
    | emissionKind_colon EmissionKind
    | enums_colon MDField
    | retainedTypes_colon MDField
    | globals_colon MDField
    | imports_colon MDField
    | macros_colon MDField
    | dwoId_colon IntLit
    | splitDebugInlining_colon BoolLit
    | debugInfoForProfiling_colon BoolLit
    | gnuPubnames_colon BoolLit
    | nameTableKind_colon name
    '''
    t[ 0 ] = Node( 'DICompileUnitField', t )

# Next
def p_DIFile(t):
    '''DIFile : not_DIFile '(' DIFileFields ')'
    '''
    t[ 0 ] = Node( 'DIFile', t )

# Next
def p_DIFileFields(t):
    '''DIFileFields : empty
    | DIFileFieldList
    '''
    t[ 0 ] = Node( 'DIFileFields', t )

# Next
def p_DIFileFieldList(t):
    '''DIFileFieldList : DIFileField
    | DIFileFieldList ',' DIFileField
    '''
    t[ 0 ] = Node( 'DIFileFieldList', t )

# Next
def p_DIFileField(t):
    '''DIFileField : filename_colon StringLit
    | directory_colon StringLit
    | checksumkind_colon ChecksumKind
    | checksum_colon StringLit
    '''
    t[ 0 ] = Node( 'DIFileField', t )

# Next
def p_DIBasicType(t):
    '''DIBasicType : not_DIBasicType '(' DIBasicTypeFields ')'
    '''
    t[ 0 ] = Node( 'DIBasicType', t )

# Next
def p_DIBasicTypeFields(t):
    '''DIBasicTypeFields : empty
    | DIBasicTypeFieldList
    '''
    t[ 0 ] = Node( 'DIBasicTypeFields', t )

# Next
def p_DIBasicTypeFieldList(t):
    '''DIBasicTypeFieldList : DIBasicTypeField
    | DIBasicTypeFieldList ',' DIBasicTypeField
    '''
    t[ 0 ] = Node( 'DIBasicTypeFieldList', t )

# Next
def p_DIBasicTypeField(t):
    '''DIBasicTypeField : TagField
    | NameField
    | SizeField
    | AlignField
    | encoding_colon DwarfAttEncoding
    '''
    t[ 0 ] = Node( 'DIBasicTypeField', t )

# Next
def p_DISubroutineType(t):
    '''DISubroutineType : not_DISubroutineType '(' DISubroutineTypeFields ')'
    '''
    t[ 0 ] = Node( 'DISubroutineType', t )

# Next
def p_DISubroutineTypeFields(t):
    '''DISubroutineTypeFields : empty
    | DISubroutineTypeFieldList
    '''
    t[ 0 ] = Node( 'DISubroutineTypeFields', t )

# Next
def p_DISubroutineTypeFieldList(t):
    '''DISubroutineTypeFieldList : DISubroutineTypeField
    | DISubroutineTypeFieldList ',' DISubroutineTypeField
    '''
    t[ 0 ] = Node( 'DISubroutineTypeFieldList', t )

# Next
def p_DISubroutineTypeField(t):
    '''DISubroutineTypeField : FlagsField
    | cc_colon DwarfCC
    | types_colon MDField
    '''
    t[ 0 ] = Node( 'DISubroutineTypeField', t )

# Next
def p_DIDerivedType(t):
    '''DIDerivedType : not_DIDerivedType '(' DIDerivedTypeFields ')'
    '''
    t[ 0 ] = Node( 'DIDerivedType', t )

# Next
def p_DIDerivedTypeFields(t):
    '''DIDerivedTypeFields : empty
    | DIDerivedTypeFieldList
    '''
    t[ 0 ] = Node( 'DIDerivedTypeFields', t )

# Next
def p_DIDerivedTypeFieldList(t):
    '''DIDerivedTypeFieldList : DIDerivedTypeField
    | DIDerivedTypeFieldList ',' DIDerivedTypeField
    '''
    t[ 0 ] = Node( 'DIDerivedTypeFieldList', t )

# Next
def p_DIDerivedTypeField(t):
    '''DIDerivedTypeField : TagField
    | NameField
    | ScopeField
    | FileField
    | LineField
    | BaseTypeField
    | SizeField
    | AlignField
    | OffsetField
    | FlagsField
    | extraData_colon MDField
    | dwarfAddressSpace_colon IntLit
    '''
    t[ 0 ] = Node( 'DIDerivedTypeField', t )

# Next
def p_DICompositeType(t):
    '''DICompositeType : not_DICompositeType '(' DICompositeTypeFields ')'
    '''
    t[ 0 ] = Node( 'DICompositeType', t )

# Next
def p_DICompositeTypeFields(t):
    '''DICompositeTypeFields : empty
    | DICompositeTypeFieldList
    '''
    t[ 0 ] = Node( 'DICompositeTypeFields', t )

# Next
def p_DICompositeTypeFieldList(t):
    '''DICompositeTypeFieldList : DICompositeTypeField
    | DICompositeTypeFieldList ',' DICompositeTypeField
    '''
    t[ 0 ] = Node( 'DICompositeTypeFieldList', t )

# Next
def p_DICompositeTypeField(t):
    '''DICompositeTypeField : TagField
    | NameField
    | ScopeField
    | FileField
    | LineField
    | BaseTypeField
    | SizeField
    | AlignField
    | OffsetField
    | FlagsField
    | elements_colon MDField
    | runtimeLang_colon DwarfLang
    | vtableHolder_colon MDField
    | TemplateParamsField
    | identifier_colon StringLit
    | discriminator_colon MDField
    '''
    t[ 0 ] = Node( 'DICompositeTypeField', t )

# Next
def p_DISubrange(t):
    '''DISubrange : not_DISubrange '(' DISubrangeFields ')'
    '''
    t[ 0 ] = Node( 'DISubrange', t )

# Next
def p_DISubrangeFields(t):
    '''DISubrangeFields : empty
    | DISubrangeFieldList
    '''
    t[ 0 ] = Node( 'DISubrangeFields', t )

# Next
def p_DISubrangeFieldList(t):
    '''DISubrangeFieldList : DISubrangeField
    | DISubrangeFieldList ',' DISubrangeField
    '''
    t[ 0 ] = Node( 'DISubrangeFieldList', t )

# Next
def p_DISubrangeField(t):
    '''DISubrangeField : count_colon IntOrMDField
    | lowerBound_colon IntLit
    '''
    t[ 0 ] = Node( 'DISubrangeField', t )

# Next
def p_DIEnumerator(t):
    '''DIEnumerator : not_DIEnumerator '(' DIEnumeratorFields ')'
    '''
    t[ 0 ] = Node( 'DIEnumerator', t )

# Next
def p_DIEnumeratorFields(t):
    '''DIEnumeratorFields : empty
    | DIEnumeratorFieldList
    '''
    t[ 0 ] = Node( 'DIEnumeratorFields', t )

# Next
def p_DIEnumeratorFieldList(t):
    '''DIEnumeratorFieldList : DIEnumeratorField
    | DIEnumeratorFieldList ',' DIEnumeratorField
    '''
    t[ 0 ] = Node( 'DIEnumeratorFieldList', t )

# Next
def p_DIEnumeratorField(t):
    '''DIEnumeratorField : NameField
    | value_colon IntLit
    | isUnsigned_colon BoolLit
    '''
    t[ 0 ] = Node( 'DIEnumeratorField', t )

# Next
def p_DITemplateTypeParameter(t):
    '''DITemplateTypeParameter : not_DITemplateTypeParameter '(' DITemplateTypeParameterFields ')'
    '''
    t[ 0 ] = Node( 'DITemplateTypeParameter', t )

# Next
def p_DITemplateTypeParameterFields(t):
    '''DITemplateTypeParameterFields : empty
    | DITemplateTypeParameterFieldList
    '''
    t[ 0 ] = Node( 'DITemplateTypeParameterFields', t )

# Next
def p_DITemplateTypeParameterFieldList(t):
    '''DITemplateTypeParameterFieldList : DITemplateTypeParameterField
    | DITemplateTypeParameterFieldList ',' DITemplateTypeParameterField
    '''
    t[ 0 ] = Node( 'DITemplateTypeParameterFieldList', t )

# Next
def p_DITemplateTypeParameterField(t):
    '''DITemplateTypeParameterField : NameField
    | TypeField
    '''
    t[ 0 ] = Node( 'DITemplateTypeParameterField', t )

# Next
def p_DITemplateValueParameter(t):
    '''DITemplateValueParameter : not_DITemplateValueParameter '(' DITemplateValueParameterFields ')'
    '''
    t[ 0 ] = Node( 'DITemplateValueParameter', t )

# Next
def p_DITemplateValueParameterFields(t):
    '''DITemplateValueParameterFields : empty
    | DITemplateValueParameterFieldList
    '''
    t[ 0 ] = Node( 'DITemplateValueParameterFields', t )

# Next
def p_DITemplateValueParameterFieldList(t):
    '''DITemplateValueParameterFieldList : DITemplateValueParameterField
    | DITemplateValueParameterFieldList ',' DITemplateValueParameterField
    '''
    t[ 0 ] = Node( 'DITemplateValueParameterFieldList', t )

# Next
def p_DITemplateValueParameterField(t):
    '''DITemplateValueParameterField : TagField
    | NameField
    | TypeField
    | value_colon MDField
    '''
    t[ 0 ] = Node( 'DITemplateValueParameterField', t )

# Next
def p_DINamespace(t):
    '''DINamespace : not_DINamespace '(' DINamespaceFields ')'
    '''
    t[ 0 ] = Node( 'DINamespace', t )

# Next
def p_DINamespaceFields(t):
    '''DINamespaceFields : empty
    | DINamespaceFieldList
    '''
    t[ 0 ] = Node( 'DINamespaceFields', t )

# Next
def p_DINamespaceFieldList(t):
    '''DINamespaceFieldList : DINamespaceField
    | DINamespaceFieldList ',' DINamespaceField
    '''
    t[ 0 ] = Node( 'DINamespaceFieldList', t )

# Next
def p_DINamespaceField(t):
    '''DINamespaceField : ScopeField
    | NameField
    | exportSymbols_colon BoolLit
    '''
    t[ 0 ] = Node( 'DINamespaceField', t )

# Next
def p_DIGlobalVariable(t):
    '''DIGlobalVariable : not_DIGlobalVariable '(' DIGlobalVariableFields ')'
    '''
    t[ 0 ] = Node( 'DIGlobalVariable', t )

# Next
def p_DIGlobalVariableFields(t):
    '''DIGlobalVariableFields : empty
    | DIGlobalVariableFieldList
    '''
    t[ 0 ] = Node( 'DIGlobalVariableFields', t )

# Next
def p_DIGlobalVariableFieldList(t):
    '''DIGlobalVariableFieldList : DIGlobalVariableField
    | DIGlobalVariableFieldList ',' DIGlobalVariableField
    '''
    t[ 0 ] = Node( 'DIGlobalVariableFieldList', t )

# Next
def p_DIGlobalVariableField(t):
    '''DIGlobalVariableField : NameField
    | ScopeField
    | LinkageNameField
    | FileField
    | LineField
    | TypeField
    | IsLocalField
    | IsDefinitionField
    | DeclarationField
    | AlignField
    '''
    t[ 0 ] = Node( 'DIGlobalVariableField', t )

# Next
def p_DISubprogram(t):
    '''DISubprogram : not_DISubprogram '(' DISubprogramFields ')'
    '''
    t[ 0 ] = Node( 'DISubprogram', t )

# Next
def p_DISubprogramFields(t):
    '''DISubprogramFields : empty
    | DISubprogramFieldList
    '''
    t[ 0 ] = Node( 'DISubprogramFields', t )

# Next
def p_DISubprogramFieldList(t):
    '''DISubprogramFieldList : DISubprogramField
    | DISubprogramFieldList ',' DISubprogramField
    '''
    t[ 0 ] = Node( 'DISubprogramFieldList', t )

# Next
# Never mentioned in the grammar from the web site, a 
# DISubprogramField can also start with "spFlags:" which
# is mentioned nowhere. I have added this to the
# FlagsField non-terminal - hope that is right.
# It's not clear what the exact flag list is, but it
# is clear that it is NOT the same exact set as what
# is OK for "flags:". So we will just accept "name".
# (No, it's DIFlagList becuse it allows '|')
# Same with "retainedNodes:"
def p_DISubprogramField(t):
    '''DISubprogramField : NameField
    | ScopeField
    | LinkageNameField
    | FileField
    | LineField
    | TypeField
    | IsLocalField
    | IsDefinitionField
    | scopeLine_colon IntLit
    | containingType_colon MDField
    | virtuality_colon DwarfVirtuality
    | virtualIndex_colon IntLit
    | thisAdjustment_colon IntLit
    | FlagsField
    | IsOptimizedField
    | unit_colon MDField
    | TemplateParamsField
    | DeclarationField
    | variables_colon MDField
    | thrownTypes_colon MDField
    | spFlags_colon BILLflaglist
    | retainedNodes_colon metadata_id
    '''
    t[ 0 ] = Node( 'DISubprogramField', t )

# Next
# Since spFlags was not in the grammar on the internet
# we can't be sure what the possible flags ARE without 
# jumoing into their C++ code. So just come here and add them
# as you bump into them, I guess.
def p_BILLflaglist(t):
    '''BILLflaglist : DISPFlagDefinition
    | DISPFlagLocalToUnit '|' DISPFlagDefinition
    '''
    t[ 0 ] = Node( 'BILLflaglist', t )

# Next
def p_DILexicalBlock(t):
    '''DILexicalBlock : not_DILexicalBlock '(' DILexicalBlockFields ')'
    '''
    t[ 0 ] = Node( 'DILexicalBlock', t )

# Next
def p_DILexicalBlockFields(t):
    '''DILexicalBlockFields : empty
    | DILexicalBlockFieldList
    '''
    t[ 0 ] = Node( 'DILexicalBlockFields', t )

# Next
def p_DILexicalBlockFieldList(t):
    '''DILexicalBlockFieldList : DILexicalBlockField
    | DILexicalBlockFieldList ',' DILexicalBlockField
    '''
    t[ 0 ] = Node( 'DILexicalBlockFieldList', t )

# Next
def p_DILexicalBlockField(t):
    '''DILexicalBlockField : ScopeField
    | FileField
    | LineField
    | ColumnField
    '''
    t[ 0 ] = Node( 'DILexicalBlockField', t )

# Next
def p_DILexicalBlockFile(t):
    '''DILexicalBlockFile : not_DILexicalBlockFile '(' DILexicalBlockFileFields ')'
    '''
    t[ 0 ] = Node( 'DILexicalBlockFile', t )

# Next
def p_DILexicalBlockFileFields(t):
    '''DILexicalBlockFileFields : empty
    | DILexicalBlockFileFieldList
    '''
    t[ 0 ] = Node( 'DILexicalBlockFileFields', t )

# Next
def p_DILexicalBlockFileFieldList(t):
    '''DILexicalBlockFileFieldList : DILexicalBlockFileField
    | DILexicalBlockFileFieldList ',' DILexicalBlockFileField
    '''
    t[ 0 ] = Node( 'DILexicalBlockFileFieldList', t )

# Next
def p_DILexicalBlockFileField(t):
    '''DILexicalBlockFileField : ScopeField
    | FileField
    | discriminator_colon IntLit
    '''
    t[ 0 ] = Node( 'DILexicalBlockFileField', t )

# Next
def p_DILocation(t):
    '''DILocation : not_DILocation '(' DILocationFields ')'
    '''
    t[ 0 ] = Node( 'DILocation', t )

# Next
def p_DILocationFields(t):
    '''DILocationFields : empty
    | DILocationFieldList
    '''
    t[ 0 ] = Node( 'DILocationFields', t )

# Next
def p_DILocationFieldList(t):
    '''DILocationFieldList : DILocationField
    | DILocationFieldList ',' DILocationField
    '''
    t[ 0 ] = Node( 'DILocationFieldList', t )

# Next
def p_DILocationField(t):
    '''DILocationField : LineField
    | ColumnField
    | ScopeField
    | inlinedAt_colon MDField
    '''
    t[ 0 ] = Node( 'DILocationField', t )

# Next
def p_DILocalVariable(t):
    '''DILocalVariable : not_DILocalVariable '(' DILocalVariableFields ')'
    '''
    t[ 0 ] = Node( 'DILocalVariable', t )

# Next
def p_DILocalVariableFields(t):
    '''DILocalVariableFields : empty
    | DILocalVariableFieldList
    '''
    t[ 0 ] = Node( 'DILocalVariableFields', t )

# Next
def p_DILocalVariableFieldList(t):
    '''DILocalVariableFieldList : DILocalVariableField
    | DILocalVariableFieldList ',' DILocalVariableField
    '''
    t[ 0 ] = Node( 'DILocalVariableFieldList', t )

# Next
def p_DILocalVariableField(t):
    '''DILocalVariableField : NameField
    | arg_colon IntLit
    | ScopeField
    | FileField
    | LineField
    | TypeField
    | FlagsField
    | AlignField
    '''
    t[ 0 ] = Node( 'DILocalVariableField', t )

# Next
def p_DIExpression(t):
    '''DIExpression : not_DIExpression '(' DIExpressionFields ')'
    '''
    t[ 0 ] = Node( 'DIExpression', t )

# Next
def p_DIExpressionFields(t):
    '''DIExpressionFields : empty
    | DIExpressionFieldList
    '''
    t[ 0 ] = Node( 'DIExpressionFields', t )

# Next
def p_DIExpressionFieldList(t):
    '''DIExpressionFieldList : DIExpressionField
    | DIExpressionFieldList ',' DIExpressionField
    '''
    t[ 0 ] = Node( 'DIExpressionFieldList', t )

# Next
def p_DIExpressionField(t):
    '''DIExpressionField : int_lit
    | DwarfOp
    '''
    t[ 0 ] = Node( 'DIExpressionField', t )

# Next
def p_DIGlobalVariableExpression(t):
    '''DIGlobalVariableExpression : not_DIGlobalVariableExpression '(' DIGlobalVariableExpressionFields ')'
    '''
    t[ 0 ] = Node( 'DIGlobalVariableExpression', t )

# Next
def p_DIGlobalVariableExpressionFields(t):
    '''DIGlobalVariableExpressionFields : empty
    | DIGlobalVariableExpressionFieldList
    '''
    t[ 0 ] = Node( 'DIGlobalVariableExpressionFields', t )

# Next
def p_DIGlobalVariableExpressionFieldList(t):
    '''DIGlobalVariableExpressionFieldList : DIGlobalVariableExpressionField
    | DIGlobalVariableExpressionFieldList ',' DIGlobalVariableExpressionField
    '''
    t[ 0 ] = Node( 'DIGlobalVariableExpressionFieldList', t )

# Next
# Issue here. The production uses "var:" and "expr:" as
# literal strings. The scanner will hand them to us as labels.
# They were not included in the token list from the site
# that has the grammar, so I have added "var_colon" and
# "expr_colon" as tokens.
def p_DIGlobalVariableExpressionField(t):
    '''DIGlobalVariableExpressionField : var_colon MDField
    | expr_colon MDField
    '''
    t[ 0 ] = Node( 'DIGlobalVariableExpression', t )

# Next
def p_DIObjCProperty(t):
    '''DIObjCProperty : not_DIObjCProperty '(' DIObjCPropertyFields ')'
    '''
    t[ 0 ] = Node( 'DIObjCProperty', t )

# Next
def p_DIObjCPropertyFields(t):
    '''DIObjCPropertyFields : empty
    | DIObjCPropertyFieldList
    '''
    t[ 0 ] = Node( 'DIObjCPropertyFields', t )

# Next
def p_DIObjCPropertyFieldList(t):
    '''DIObjCPropertyFieldList : DIObjCPropertyField
    | DIObjCPropertyFieldList ',' DIObjCPropertyField
    '''
    t[ 0 ] = Node( 'DIObjCPropertyFieldList', t )

# Next
def p_DIObjCPropertyField(t):
    '''DIObjCPropertyField : NameField
    | FileField
    | LineField
    | setter_colon StringLit
    | getter_colon StringLit
    | attributes_colon IntLit
    | TypeField
    '''
    t[ 0 ] = Node( 'DIObjCPropertyField', t )

# Next
def p_DIImportedEntity(t):
    '''DIImportedEntity : not_DIImportedEntity '(' DIImportedEntityFields ')'
    '''
    t[ 0 ] = Node( 'DIImportedEntity', t )

# Next
def p_DIImportedEntityFields(t):
    '''DIImportedEntityFields : empty
    | DIImportedEntityFieldList
    '''
    t[ 0 ] = Node( 'DIImportedEntityFields', t )

# Next
def p_DIImportedEntityFieldList(t):
    '''DIImportedEntityFieldList : DIImportedEntityField
    | DIImportedEntityFieldList ',' DIImportedEntityField
    '''
    t[ 0 ] = Node( 'DIImportedEntityFieldList', t )

# Next
def p_DIImportedEntityField(t):
    '''DIImportedEntityField : TagField
    | ScopeField
    | entity_colon MDField
    | FileField
    | LineField
    | NameField
    '''
    t[ 0 ] = Node( 'DIImportedEntityField', t )

# Next
def p_DIMacro(t):
    '''DIMacro : not_DIMacro '(' DIMacroFields ')'
    '''
    t[ 0 ] = Node( 'DIMacro', t )

# Next
def p_DIMacroFields(t):
    '''DIMacroFields : empty
    | DIMacroFieldList
    '''
    t[ 0 ] = Node( 'DIMacroFields', t )

# Next
def p_DIMacroFieldList(t):
    '''DIMacroFieldList : DIMacroField
    | DIMacroFieldList ',' DIMacroField
    '''
    t[ 0 ] = Node( 'DIMacroFieldList', t )

# Next
def p_DIMacroField(t):
    '''DIMacroField : TypeMacinfoField
    | LineField
    | NameField
    | value_colon StringLit
    '''
    t[ 0 ] = Node( 'DIMacroField', t )

# Next
def p_DIMacroFile(t):
    '''DIMacroFile : not_DIMacroFile '(' DIMacroFileFields ')'
    '''
    t[ 0 ] = Node( 'DIMacroFile', t )

# Next
def p_DIMacroFileFields(t):
    '''DIMacroFileFields : empty
    | DIMacroFileFieldList
    '''
    t[ 0 ] = Node( 'DIMacroFileFields', t )

# Next
def p_DIMacroFileFieldList(t):
    '''DIMacroFileFieldList : DIMacroFileField
    | DIMacroFileFieldList ',' DIMacroFileField
    '''
    t[ 0 ] = Node( 'DIMacroFileFieldList', t )

# Next
def p_DIMacroFileField(t):
    '''DIMacroFileField : TypeMacinfoField
    | LineField
    | FileField
    | nodes_colon MDField
    '''
    t[ 0 ] = Node( 'DIMacroFileField', t )

# Next
def p_FileField(t):
    '''FileField : file_colon MDField
    '''
    t[ 0 ] = Node( 'FileField', t )

# Next
def p_IsOptimizedField(t):
    '''IsOptimizedField : isOptimized_colon BoolLit
    '''
    t[ 0 ] = Node( 'IsOptimizedField', t )

# Next
def p_TagField(t):
    '''TagField : tag_colon DwarfTag
    '''
    t[ 0 ] = Node( 'TagField', t )

# Next
def p_NameField(t):
    '''NameField : name_colon StringLit
    '''
    t[ 0 ] = Node( 'NameField', t )

# Next
def p_SizeField(t):
    '''SizeField : size_colon IntLit
    '''
    t[ 0 ] = Node( 'SizeField', t )

# Next
def p_AlignField(t):
    '''AlignField : align_colon IntLit
    '''
    t[ 0 ] = Node( 'AlignField', t )

# Next
def p_FlagsField(t):
    '''FlagsField : flags_colon DIFlagList
    '''
    t[ 0 ] = Node( 'FlagsField', t )

# Next
def p_LineField(t):
    '''LineField : line_colon IntLit
    '''
    t[ 0 ] = Node( 'LineField', t )

# Next
def p_ScopeField(t):
    '''ScopeField : scope_colon MDField
    '''
    t[ 0 ] = Node( 'ScopeField', t )

# Next
def p_BaseTypeField(t):
    '''BaseTypeField : baseType_colon MDField
    '''
    t[ 0 ] = Node( 'BaseTypeField', t )

# Next
def p_OffsetField(t):
    '''OffsetField : offset_colon IntLit
    '''
    t[ 0 ] = Node( 'OffsetField', t )

# Next
def p_TemplateParamsField(t):
    '''TemplateParamsField : templateParams_colon MDField
    '''
    t[ 0 ] = Node( 'TemplateParamsField', t )

# Next
def p_IntOrMDField(t):
    '''IntOrMDField : int_lit
    | MDField
    '''
    t[ 0 ] = Node( 'IntOrMDField', t )

# Next
def p_TypeField(t):
    '''TypeField : type_colon MDField
    '''
    t[ 0 ] = Node( 'TypeField', t )

# Next
def p_LinkageNameField(t):
    '''LinkageNameField : linkageName_colon StringLit
    '''
    t[ 0 ] = Node( 'LinkageNameField', t )

# Next
def p_IsLocalField(t):
    '''IsLocalField : isLocal_colon BoolLit
    '''
    t[ 0 ] = Node( 'IsLocalField', t )

# Next
def p_IsDefinitionField(t):
    '''IsDefinitionField : isDefinition_colon BoolLit
    '''
    t[ 0 ] = Node( 'IsDefinitionField', t )

# Next
def p_DeclarationField(t):
    '''DeclarationField : declaration_colon MDField
    '''
    t[ 0 ] = Node( 'DeclarationField', t )

# Next
def p_ColumnField(t):
    '''ColumnField : column_colon IntLit
    '''
    t[ 0 ] = Node( 'ColumnField', t )

# Next
def p_TypeMacinfoField(t):
    '''TypeMacinfoField : type_colon DwarfMacinfo
    '''
    t[ 0 ] = Node( 'TypeMacinfoField', t )

# Next
def p_ChecksumKind(t):
    '''ChecksumKind : checksum_kind
    '''
    t[ 0 ] = Node( 'ChecksumKind', t )

# Next
def p_DIFlagList(t):
    '''DIFlagList : DIFlag
    | DIFlagList '|' DIFlag
    '''
    t[ 0 ] = Node( 'DIFlagList', t )

# Next
def p_DIFlag(t):
    '''DIFlag : IntLit
    | di_flag
    '''
    t[ 0 ] = Node( 'DIFlag', t )

# Next
def p_DwarfAttEncoding(t):
    '''DwarfAttEncoding : IntLit
    | dwarf_att_encoding
    '''
    t[ 0 ] = Node( 'DwarfAttEncoding', t )

# Next
def p_DwarfCC(t):
    '''DwarfCC : IntLit
    | dwarf_cc
    '''
    t[ 0 ] = Node( 'DwarfCC', t )

# Next
def p_DwarfLang(t):
    '''DwarfLang : IntLit
    | dwarf_lang
    '''
    t[ 0 ] = Node( 'DwarfLang', t )

# Next
def p_DwarfMacinfo(t):
    '''DwarfMacinfo : IntLit
    | dwarf_macinfo
    '''
    t[ 0 ] = Node( 'DwarfMacinfo', t )

# Next
def p_DwarfOp(t):
    '''DwarfOp : dwarf_op
    '''
    t[ 0 ] = Node( 'DwarfOp', t )

# Next
def p_DwarfTag(t):
    '''DwarfTag : IntLit
    | dwarf_tag
    '''
    t[ 0 ] = Node( 'DwarfTag', t )

# Next
def p_DwarfVirtuality(t):
    '''DwarfVirtuality : IntLit
    | dwarf_virtuality
    '''
    t[ 0 ] = Node( 'DwarfVirtuality', t )

# Next
def p_EmissionKind(t):
    '''EmissionKind : IntLit
    | FullDebug
    | LineTablesOnly
    | NoDebug
    '''
    t[ 0 ] = Node( 'EmissionKind', t )

# Next
def p_TypeValues(t):
    '''TypeValues : empty
    | TypeValueList
    '''
    t[ 0 ] = Node( 'TypeValues', t )

# Next
def p_TypeValueList(t):
    '''TypeValueList : TypeValue
    | TypeValueList TypeValue
    '''
    t[ 0 ] = Node( 'TypeValueList', t )

# Next
def p_CommaSepTypeValueList(t):
    '''CommaSepTypeValueList : TypeValue
    | CommaSepTypeValueList ',' TypeValue
    '''
    t[ 0 ] = Node( 'CommaSepTypeValueList', t )

# Next
def p_TypeValue(t):
    '''TypeValue : Type Value
    '''
    t[ 0 ] = Node( 'TypeValue', t )

# Next
def p_TypeConsts(t):
    '''TypeConsts : empty
    | TypeConstList
    '''
    t[ 0 ] = Node( 'TypeConsts', t )

# Next
def p_TypeConstList(t):
    '''TypeConstList : TypeConst
    | TypeConstList ',' TypeConst
    '''
    t[ 0 ] = Node( 'TypeConstList', t )

# Next
def p_TypeConst(t):
    '''TypeConst : Type Constant
    '''
    t[ 0 ] = Node( 'TypeConst', t )

# Next
def p_Alignment(t):
    '''Alignment : align int_lit
    '''
    t[ 0 ] = Node( 'Alignment', t )

# Next
def p_AllocSize(t):
    '''AllocSize : allocsize '(' int_lit ')'
    | allocsize '(' int_lit ',' int_lit ')'
    '''
    t[ 0 ] = Node( 'AllocSize', t )

# Next
def p_Args(t):
    '''Args : empty
    | elipsis
    | ArgList
    | ArgList ',' elipsis
    '''
    t[ 0 ] = Node( 'Args', t )

# Next
def p_ArgList(t):
    '''ArgList : Arg
    | ArgList ',' Arg
    '''
    t[ 0 ] = Node( 'ArgList', t )

# Next
def p_Arg(t):
    '''Arg : ConcreteType ParamAttrs Value
    | MetadataType Metadata
    '''
    t[ 0 ] = Node( 'Arg', t )

# Next
def p_AtomicOrdering(t):
    '''AtomicOrdering : acq_rel
    | acquire
    | monotonic
    | release
    | seq_cst
    | unordered
    '''
    t[ 0 ] = Node( 'AtomicOrdering', t )

# Next
def p_OptCallingConv(t):
    '''OptCallingConv : empty
    | CallingConv
    '''
    t[ 0 ] = Node( 'OptCallingConv', t )

# Next
def p_CallingConv(t):
    '''CallingConv : amdgpu_cs
    | amdgpu_es
    | amdgpu_gs
    | amdgpu_hs
    | amdgpu_kernel
    | amdgpu_ls
    | amdgpu_ps
    | amdgpu_vs
    | anyregcc
    | arm_aapcs_vfpcc
    | arm_aapcscc
    | arm_apcscc
    | avr_intrcc
    | avr_signalcc
    | ccc
    | coldcc
    | cxx_fast_tlscc
    | fastcc
    | ghccc
    | hhvm_ccc
    | hhvmcc
    | intel_ocl_bicc
    | msp430_intrcc
    | preserve_allcc
    | preserve_mostcc
    | ptx_device
    | ptx_kernel
    | spir_func
    | spir_kernel
    | swiftcc
    | webkit_jscc
    | win64cc
    | x86_64_sysvcc
    | x86_fastcallcc
    | x86_intrcc
    | x86_regcallcc
    | x86_stdcallcc
    | x86_thiscallcc
    | x86_vectorcallcc
    | cc int_lit
    '''
    t[ 0 ] = Node( 'CallingConv', t )

# Next
def p_Dereferenceable(t):
    '''Dereferenceable : dereferenceable '(' int_lit ')'
    | dereferenceable_or_null '(' int_lit ')'
    '''
    t[ 0 ] = Node( 'Dereferenceable', t )

# Next
def p_OptExact(t):
    '''OptExact : empty
    | exact
    '''
    t[ 0 ] = Node( 'OptExact', t )

# Next
def p_ExceptionArgs(t):
    '''ExceptionArgs : empty
    | ExceptionArgList
    '''
    t[ 0 ] = Node( 'ExceptionArgs', t )

# Next
def p_ExceptionArgList(t):
    '''ExceptionArgList : ExceptionArg
    | ExceptionArgList ',' ExceptionArg
    '''
    t[ 0 ] = Node( 'ExceptionArgList', t )

# Next
def p_ExceptionArg(t):
    '''ExceptionArg : ConcreteType Value
    | MetadataType Metadata
    '''
    t[ 0 ] = Node( 'ExceptionArg', t )

# Next
def p_ExceptionScope(t):
    '''ExceptionScope : NoneConst
    | LocalIdent
    '''
    t[ 0 ] = Node( 'ExceptionScope', t )

# Next
def p_FastMathFlags(t):
    '''FastMathFlags : empty
    | FastMathFlagList
    '''
    t[ 0 ] = Node( 'FastMathFlags', t )

# Next
def p_FastMathFlagList(t):
    '''FastMathFlagList : FastMathFlag
    | FastMathFlagList FastMathFlag
    '''
    t[ 0 ] = Node( 'FastMathFlagList', t )

# Next
def p_FastMathFlag(t):
    '''FastMathFlag : afn
    | arcp
    | contract
    | fast
    | ninf
    | nnan
    | nsz
    | reassoc
    '''
    t[ 0 ] = Node( 'FastMathFlag', t )

# Next
def p_FPred(t):
    '''FPred : false_kw
    | oeq
    | oge
    | ogt
    | ole
    | olt
    | one
    | ord
    | true_kw
    | ueq
    | uge
    | ugt
    | ule
    | ult
    | une
    | uno
    '''
    t[ 0 ] = Node( 'FPred', t )

# Next
def p_FuncAttrs(t):
    '''FuncAttrs : empty
    | FuncAttrList
    '''
    t[ 0 ] = Node( 'FuncAttrs', t )

# Next
def p_FuncAttrList(t):
    '''FuncAttrList : FuncAttr
    | FuncAttrList FuncAttr
    '''
    t[ 0 ] = Node( 'FuncAttrList', t )

# "nofree" appears in version 9.0
# Next
def p_FuncAttr(t):
    '''FuncAttr : AttrGroupID
    | align '=' int_lit
    | alignstack '=' int_lit
    | Alignment
    | AllocSize
    | StackAlignment
    | StringLit
    | StringLit '=' StringLit
    | alwaysinline
    | argmemonly
    | builtin
    | cold
    | convergent
    | inaccessiblemem_or_argmemonly
    | inaccessiblememonly
    | inlinehint
    | jumptable
    | minsize
    | naked
    | nobuiltin
    | noduplicate
    | nofree
    | noimplicitfloat
    | noinline
    | nonlazybind
    | norecurse
    | noredzone
    | noreturn
    | nounwind
    | optnone
    | optsize
    | readnone
    | readonly
    | returns_twice
    | safestack
    | sanitize_address
    | sanitize_hwaddress
    | sanitize_memory
    | sanitize_thread
    | speculatable
    | ssp
    | sspreq
    | sspstrong
    | strictfp
    | uwtable
    | writeonly
    '''
    t[ 0 ] = Node( 'FuncAttr', t )

# Next
def p_OptInBounds(t):
    '''OptInBounds : empty
    | inbounds
    '''
    t[ 0 ] = Node( 'OptInBounds', t )

# Next
def p_Indices(t):
    '''Indices : empty
    | ',' IndexList
    '''
    t[ 0 ] = Node( 'Indices', t )

# Next
def p_IndexList(t):
    '''IndexList : Index
    | IndexList ',' Index
    '''
    t[ 0 ] = Node( 'IndexList', t )

# Next
def p_Index(t):
    '''Index : int_lit
    '''
    t[ 0 ] = Node( 'Index', t )

# Next
def p_IPred(t):
    '''IPred : eq
    | ne
    | sge
    | sgt
    | sle
    | slt
    | uge
    | ugt
    | ule
    | ult
    '''
    t[ 0 ] = Node( 'IPred', t )

# Next
def p_OperandBundles(t):
    '''OperandBundles : empty
    | '[' OperandBundleList ']'
    '''
    t[ 0 ] = Node( 'OperandBundles', t )

# Next
def p_OperandBundleList(t):
    '''OperandBundleList : OperandBundle
    | OperandBundleList OperandBundle
    '''
    t[ 0 ] = Node( 'OperandBundleList', t )

# Next
def p_OperandBundle(t):
    '''OperandBundle : StringLit '(' TypeValues ')'
    '''
    t[ 0 ] = Node( 'OperandBundle', t )

# Next
def p_OverflowFlags(t):
    '''OverflowFlags : empty
    | OverflowFlagList
    '''
    t[ 0 ] = Node( 'OverflowFlags', t )

# Next
def p_OverflowFlagList(t):
    '''OverflowFlagList : OverflowFlag
    | OverflowFlagList OverflowFlag
    '''
    t[ 0 ] = Node( 'OverflowFlagList', t )

# Next
def p_OverflowFlag(t):
    '''OverflowFlag : nsw
    | nuw
    '''
    t[ 0 ] = Node( 'OverflowFlag', t )

# Next
def p_ParamAttrs(t):
    '''ParamAttrs : empty
    | ParamAttrList
    '''
    t[ 0 ] = Node( 'ParamAttrs', t )

# Next
def p_ParamAttrList(t):
    '''ParamAttrList : ParamAttr
    | ParamAttrList ParamAttr
    '''
    t[ 0 ] = Node( 'ParamAttrList', t )

# LLVM 9.01 seems to have added "immarg", "nofree"
# LLVM 9.01 (in the 10 documentation) adds an optional type on "byval"
# Next
def p_ParamAttr(t):
    '''ParamAttr : Alignment
    | Dereferenceable
    | StringLit
    | byval MaybeByvalType
    | immarg
    | inalloca
    | inreg
    | nest
    | noalias
    | nocapture
    | nofree
    | nonnull
    | readnone
    | readonly
    | returned
    | signext
    | sret
    | swifterror
    | swiftself
    | writeonly
    | zeroext
    '''
    t[ 0 ] = Node( 'ParamAttr', t )

# See above. 
# Next
def p_MaybeByvalType(t):
    '''MaybeByvalType : empty
    | '(' Type ')'
    '''
    t[ 0 ] = Node( 'MaybeByvalType', t )
    
# Next
def p_Params(t):
    '''Params : empty
    | elipsis
    | ParamList
    | ParamList ',' elipsis
    '''
    t[ 0 ] = Node( 'Params', t )

# Next
def p_ParamList(t):
    '''ParamList : Param
    | ParamList ',' Param
    '''
    t[ 0 ] = Node( 'ParamList', t )

# Next
def p_Param(t):
    ''' Param : Type ParamAttrs
    | Type ParamAttrs LocalIdent
    '''
    t[ 0 ] = Node( 'Param', t )

# Next
def p_ReturnAttrs(t):
    '''ReturnAttrs : empty
    | ReturnAttrList
    '''
    t[ 0 ] = Node( 'ReturnAttrs', t )

# Next
def p_ReturnAttrList(t):
    '''ReturnAttrList : ReturnAttr
    | ReturnAttrList ReturnAttr
    '''
    t[ 0 ] = Node( 'ReturnAttrList', t )

# Next
def p_ReturnAttr(t):
    '''ReturnAttr : Alignment
    | Dereferenceable
    | StringLit
    | inreg
    | noalias
    | nonnull
    | signext
    | zeroext
    '''
    t[ 0 ] = Node( 'ReturnAttr', t )

# Next
def p_StackAlignment(t):
    '''StackAlignment : alignstack '(' int_lit ')'
    '''
    t[ 0 ] = Node( 'StackAlignment', t )

# Next
def p_OptSyncScope(t):
    '''OptSyncScope : empty
    | syncscope '(' StringLit ')'
    '''
    t[ 0 ] = Node( 'OptSyncScope', t )

# Next
def p_OptVolatile(t):
    '''OptVolatile : empty
    | volatile_kw
    '''
    t[ 0 ] = Node( 'OptVolatile', t )

# ============================================================
# The tokens that are not really tokens...
# ============================================================

#def p_quoted_name(t):
#    '''quoted_name : quoted_string'''
#    t[ 0 ] = Node( 'quoted_name', t )

def p_string_lit(t):
    '''string_lit : quoted_string'''
    t[ 0 ] = Node( 'string_lit', t )

#def p_id(t):
#    '''id : decimals'''
#    t[ 0 ] = Node( 'id', t )

def p_int_lit(t):
    '''int_lit : decimal_lit'''
    t[ 0 ] = Node( 'int_lit', t )

# We have to catch negative numbers in t_decimals
# and not here because they will appear as a name.
# (Yes, names can start with a minus sign???)
def p_decimal_lit(t):
    '''decimal_lit : decimals
    '''
    t[ 0 ] = Node( 'decimal_lit', t )

def p_float_lit(t):
    '''float_lit : frac_lit
    | sci_lit
    | float_hex_lit'''
    t[ 0 ] = Node( 'float_lit', t )

# ============================================================
# And finally...
# ============================================================

def p_empty(t):
    '''empty :
    '''
    t[ 0 ] = Node( '(empty)', [] )
    t[ 0 ].is_epsilon = True
    t[ 0 ].was_terminal = True

def p_error(token):
    global number_of_errors
    # print( "Syntax error at '%s'" % token.value )
    print( "Syntax error (well, grammar error) at about line " +
           str( token.lineno ) + " at or before token '" +
           token.value + "'" )
    number_of_errors = number_of_errors + 1

# ============================================================
#
# This can be used to test the scanner.
#
# ============================================================

if ( False ):
    lexer.input( testdata )
    while True:
        tok = lexer.token()
        if not tok:
            print( 'Scanner is done...\n' )
            break
        else:
            print( 'type=', tok.type, ' value=', tok.value, ' line ', tok.lineno, 'position ', tok.lexpos)
            if ( tok.type == 'SPECIAL_NAME' ):
                print( 'tok.value on the special name is \'', tok.value, '\'\n' )

# ============================================================
#
# And here's the main function to do the work.
#
# DEBUG logging gives you huge parselog.txt files.
# ERROR logging just gives syntax error information.
#
# Since we will be combining this with the instruction parser it is
# important to give these distinct names and distinct parser table
# filenames. See: https://www.dabeaz.com/ply/ply.html#ply_nn2
# and go to the bottom of section 6.1
#
# ============================================================

def inst_parse( inputstring, lex_debug = False, yacc_debug = True ):
    logging.basicConfig( level = logging.DEBUG,
                         filename = "parselog.txt", filemode = "w",
                         format = "%(filename)10s:%(lineno)4d:%(message)s" )
    log = logging.getLogger()

    i_lexer = lex.lex( debug = lex_debug, debuglog = log )
    i_parser = yacc.yacc( tabmodule = 'inst_parsertable', debug = yacc_debug, debugfile = 'inst_parser.out' )
    parsetree = i_parser.parse( inputstring, lexer = i_lexer, debug = log )
    return parsetree
