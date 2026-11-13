import exahype2.api.dslhype as dslhype
from exahype2.api import Target
import os
from enum import Enum


KernelHeaderPreamble = """#pragma once
#include "exahype2/Solver.h"
#include "exahype2/CellData.h"
#include "exahype2/VolumeIndex.h"
#include "exahype2/Functors.h"
#include "peano4/utils/Loop.h"
#include "tarch/timing/Measurement.h"
#include "tarch/timing/Watch.h"
"""
"""!
Includes every generated kernel header starts with. The DSL kernels of
all numerical schemes use only these headers.
"""

_initialised_kernel_files = set()
"""!
Kernel files (absolute paths) this Python process has already written.
The first call per file truncates it and writes the preamble, so stale
files of a previous generation never leak into the new one. Subsequent
calls append, so a scheme can generate several variants of a kernel (see
exahype2.api.Solver.NumericalScheme.NumericalSchemeGenerator) into the
same file.
"""


def _open_kernel_file(path: str, preamble: str):
    """!
    Open a generated kernel file for writing: truncate it and write the
    preamble on the first call per process, append afterwards.
    """
    path = os.path.abspath(path)
    if path in _initialised_kernel_files:
        return open(path, "a")
    _initialised_kernel_files.add(path)
    file = open(path, "w")
    file.write(preamble)
    return file



def translate_dslhype_function(
    function,
    function_namespace,
    template_parameters, 
    functor_parameters,
    pde_terms,
    output_file_name,
    target: Target,
    stateless: bool,
    function_name: str = None,
    output_directory: str = ".",
):
    """!
    function_name: str
      Name of the generated C++ function. Defaults to the name of the
      Python DSL function passed in as function.

    output_directory: str
      Directory the kernels/ subdirectory with the generated files is
      created in, usually the Peano project's directory.
    """
    if target == Target.Accelerator and stateless == False:
        raise Exception("Accelerated kernels must be stateless")

    reduced_functor_parameters = []
    for functor in functor_parameters:
        function_in_pde_terms = False
        for pde_term in pde_terms:
            if pde_term.NAME == functor.id:
                function_in_pde_terms = True
        if function_in_pde_terms:
            reduced_functor_parameters.append(functor)
    
    parser = dslhype.Parser()
    tree = parser.parse(
        function, 
        template_parameters, 
        reduced_functor_parameters, 
        pde_terms,
        namespace=function_namespace, 
        stateless=stateless,
        use_accelerator=(target==Target.Accelerator),
        function_name=function_name,
    )

    function_declaration = tree.print_declaration()
    if target == Target.Accelerator:
        function_definition = tree.print_omp()
    else:
        function_definition = tree.print_cpp()
    function_declaration_with_timer = tree.print_declaration_with_timer()
    function_definition_with_timer = tree.print_definition_with_timer()

    kernels_directory = os.path.join(output_directory, "kernels")
    os.makedirs(kernels_directory, exist_ok=True)
    header_path = os.path.join(kernels_directory, f"{output_file_name}.h")
    definitions_path = os.path.join(kernels_directory, f"{output_file_name}.cpph")

    file = _open_kernel_file(header_path, KernelHeaderPreamble)
    file.write(function_declaration)
    file.write(function_declaration_with_timer)
    file.close()

    # The definitions include the header, and the header the definitions.
    # Both carry #pragma once, so the cycle is harmless, and a scheme which
    # appends the include once more at the end of the header (e.g.
    # exahype2.api.fv.RusanovWithExplicitEuler) does no harm either.
    file = _open_kernel_file(
        definitions_path, f"""#pragma once\n#include "{output_file_name}.h"\n"""
    )
    file.write(function_definition)
    file.write(function_definition_with_timer)
    file.close()

    include_line = f"""#include "{output_file_name}.cpph"\n"""
    with open(header_path) as file:
        header = file.read()
    if include_line not in header:
        with open(header_path, "a") as file:
            file.write(include_line)

#    if target == Target.Serial:
#        file = open(f"{file_name}.h", "a")
#        file.write(function_declaration)
#        file.write(function_declaration_with_timer)
#        file.close()
#    elif target == Target.Multicore:
#        file = open(f"{file_name}.h", "a")
#        file.write("#if defined(SharedOMP)")
#        file.write(function_declaration)
#        file.write(function_declaration_with_timer)
#        file.write("#endif")
#        file.close()
#    else: # Target.Accelerator
#        file = open(f"{file_name}.h", "a")
#        file.write("#if defined(GPUOffloadingOMP)")
#        file.write(function_declaration)
#        file.write(function_declaration_with_timer)
#        file.write("#endif")
#        file.close()
#
#    if target == Target.Serial:
#        function_definition = tree.print_cpp()
#        file = open(f"{file_name}.cpph", "a")
#        file.write(function_definition)
#        file.write(function_definition_with_timer)
#        file.close()
#    elif target == Target.Multicore:
#        function_definition = tree.print_omp()
#        file = open(f"{file_name}.cpph", "a")
#        file.write("#if defined(SharedOMP)")
#        file.write(function_definition)
#        file.write(function_definition_with_timer)
#        file.write("#endif")
#        file.close()
#    else: # Target.Accelerator
#        function_definition = tree.print_omp()
#        file = open(f"{file_name}.cpph", "a")
#        file.write("#if defined(GPUOffloadingOMP)")
#        file.write(function_definition)
#        file.write(function_definition_with_timer)
#        file.write("#endif")
#        file.close()
