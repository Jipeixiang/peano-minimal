# Builds the parts of Peano that the gauge wave example needs.
#
# Peano (www.peano-framework.org) is a large framework. This file compiles
# only the 79 source files that one FD4 gauge wave run actually links,
# into the same six static libraries (3d, release mode) that a full Peano
# build provides. It then writes PeanoTargets.cmake and PeanoConfig.cmake
# into the build directory, so the code that example/gauge-wave.py
# generates finds the libraries via find_package(Peano).
#
#   cmake -S . -B build
#   cmake --build build -j
#
# The build directory has to be a direct subdirectory of this folder: the
# Python API looks there for PeanoTargets.cmake.

cmake_minimum_required(VERSION 3.21)
project(PeanoMinimum LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Peano expects a (here empty) config.h on the include path
file(WRITE "${CMAKE_BINARY_DIR}/src/config.h" "")

# Options shared by all libraries and by the generated application, as in
# a full Peano build configured with
#   -DENABLE_EXAHYPE=ON -DENABLE_EXAGRYPE=ON
#   -DENABLE_LOADBALANCING=ON -DENABLE_BLOCKSTRUCTURED=ON
# i.e. no MPI, no multithreading, no GPU.
add_library(PeanoOptions INTERFACE)
target_compile_features(PeanoOptions INTERFACE cxx_std_20)
target_compile_definitions(PeanoOptions INTERFACE
  UseToolboxLoadbalancing UseToolboxBlockstructured UseExaHyPE UseExaGRyPE
)
target_compile_options(PeanoOptions INTERFACE -w)
target_include_directories(PeanoOptions INTERFACE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_BINARY_DIR}/src
)

function(add_peano_library name extra_definitions)
  add_library(${name} STATIC ${ARGN})
  target_link_libraries(${name} PRIVATE PeanoOptions)
  target_compile_definitions(${name} PUBLIC PeanoDebug=0 NDEBUG ${extra_definitions})
  target_compile_options(${name} PUBLIC $<$<COMPILE_LANGUAGE:CXX>:-O3>)
endfunction()

set(Tarch_SOURCES
  src/tarch/Enumerator.cpp
  src/tarch/NonCriticalAssertions.cpp
  src/tarch/accelerator/Device.cpp
  src/tarch/accelerator/accelerator.cpp
  src/tarch/la/DynamicMatrix.cpp
  src/tarch/la/DynamicMatrixOperations.cpp
  src/tarch/la/GramSchmidt.cpp
  src/tarch/la/LUDecompositionDynamic.cpp
  src/tarch/la/Scalar.cpp
  src/tarch/la/ScalarOperations.cpp
  src/tarch/logging/CommandLineLogger.cpp
  src/tarch/logging/Log.cpp
  src/tarch/logging/LogFilter.cpp
  src/tarch/logging/LogFilterFileReader.cpp
  src/tarch/logging/Statistics.cpp
  src/tarch/mpi/BooleanSemaphore.cpp
  src/tarch/mpi/Lock.cpp
  src/tarch/mpi/Rank.cpp
  src/tarch/multicore/BooleanSemaphore.cpp
  src/tarch/multicore/Core.cpp
  src/tarch/multicore/Lock.cpp
  src/tarch/multicore/MultiReadSingleWriteLock.cpp
  src/tarch/multicore/MultiReadSingleWriteSemaphore.cpp
  src/tarch/multicore/RecursiveLock.cpp
  src/tarch/multicore/RecursiveSemaphore.cpp
  src/tarch/multicore/Task.cpp
  src/tarch/multicore/TaskEnumerator.cpp
  src/tarch/multicore/multicore.cpp
  src/tarch/multicore/orchestration/Hardcoded.cpp
  src/tarch/multicore/orchestration/Strategy.cpp
  src/tarch/multicore/taskfusion/FusableTasksQueue.cpp
  src/tarch/multicore/taskfusion/LogReadyTask.cpp
  src/tarch/multicore/taskfusion/ProcessOneReadyTask.cpp
  src/tarch/multicore/taskfusion/ProcessSetOfReadyTasks.cpp
  src/tarch/multicore/taskfusion/taskfusion.cpp
  src/tarch/plotter/griddata/blockstructured/PeanoBinaryPatchFileWriter.cpp
  src/tarch/plotter/griddata/blockstructured/PeanoBinaryPatchFileWriter_CellDataWriter.cpp
  src/tarch/plotter/griddata/blockstructured/PeanoBinaryPatchFileWriter_VertexDataWriter.cpp
  src/tarch/services/ServiceRepository.cpp
  src/tarch/tarch.cpp
  src/tarch/timing/GlidingAverageMeasurement.cpp
  src/tarch/timing/Measurement.cpp
  src/tarch/timing/Watch.cpp
)

set(Peano4Core3d_SOURCES
  src/peano4/DefaultStepReport.cpp
  src/peano4/RunMultipleSteps.cpp
  src/peano4/datamanagement/CellMarker.cpp
  src/peano4/datamanagement/FaceMarker.cpp
  src/peano4/datamanagement/VertexMarker.cpp
  src/peano4/grid/AutomatonState.cpp
  src/peano4/grid/GridControlEvent.cpp
  src/peano4/grid/GridStatistics.cpp
  src/peano4/grid/GridTraversalEvent.cpp
  src/peano4/grid/GridTraversalEventGenerator.cpp
  src/peano4/grid/GridVertex.cpp
  src/peano4/grid/LoadStoreComputeFlag.cpp
  src/peano4/grid/PeanoCurve.cpp
  src/peano4/grid/Spacetree.cpp
  src/peano4/grid/grid.cpp
  src/peano4/parallel/Node.cpp
  src/peano4/parallel/SpacetreeSet.cpp
  src/peano4/parallel/TreeEntry.cpp
  src/peano4/peano.cpp
  src/peano4/utils/Loop.cpp
)

set(ToolboxLoadBalancing3d_SOURCES
  src/toolbox/loadbalancing/AbstractLoadBalancing.cpp
  src/toolbox/loadbalancing/Blacklist.cpp
  src/toolbox/loadbalancing/LoadBalancingService.cpp
  src/toolbox/loadbalancing/State.cpp
  src/toolbox/loadbalancing/Statistics.cpp
  src/toolbox/loadbalancing/loadbalancing.cpp
  src/toolbox/loadbalancing/strategies/NoLoadBalancing.cpp
)

set(ToolboxBlockStructured3d_SOURCES
  src/toolbox/blockstructured/Enumeration.cpp
  src/toolbox/blockstructured/Interpolation.cpp
  src/toolbox/blockstructured/Restriction.cpp
  src/toolbox/blockstructured/HaloCopy.cpp
)

set(ExaHyPE2Core3d_SOURCES
  src/exahype2/RefinementControlService.cpp
  src/exahype2/Simulation.cpp
  src/exahype2/Solver.cpp
)

set(ExaGRyPECore3d_SOURCES
  src/exagrype/ccz4/Kernels.cpp
  src/exagrype/initialvalues/InitialValues.cpp
)

add_peano_library(Tarch_release "" ${Tarch_SOURCES})
add_peano_library(Peano4Core3d_release "Dimensions=3" ${Peano4Core3d_SOURCES})
target_link_libraries(Peano4Core3d_release PRIVATE Tarch_release)
add_peano_library(ToolboxLoadBalancing3d_release "Dimensions=3" ${ToolboxLoadBalancing3d_SOURCES})
target_link_libraries(ToolboxLoadBalancing3d_release PRIVATE Peano4Core3d_release)
add_peano_library(ToolboxBlockStructured3d_release "Dimensions=3" ${ToolboxBlockStructured3d_SOURCES})
target_link_libraries(ToolboxBlockStructured3d_release PRIVATE Peano4Core3d_release)
add_peano_library(ExaHyPE2Core3d_release "Dimensions=3" ${ExaHyPE2Core3d_SOURCES})
target_link_libraries(ExaHyPE2Core3d_release PRIVATE ToolboxLoadBalancing3d_release)
add_peano_library(ExaGRyPECore3d_release "Dimensions=3" ${ExaGRyPECore3d_SOURCES})

# Make the libraries findable from the generated application:
# find_package(Peano) reads PeanoConfig.cmake, which includes
# PeanoTargets.cmake with the imported targets Peano::<name>.
export(TARGETS PeanoOptions Tarch_release Peano4Core3d_release ToolboxLoadBalancing3d_release ToolboxBlockStructured3d_release ExaHyPE2Core3d_release ExaGRyPECore3d_release
  NAMESPACE Peano::
  FILE "${CMAKE_BINARY_DIR}/PeanoTargets.cmake"
)
file(WRITE "${CMAKE_BINARY_DIR}/PeanoConfig.cmake"
  "include(\"${CMAKE_BINARY_DIR}/PeanoTargets.cmake\")\n"
)
