// This file is part of the ExaHyPE2 project. For conditions of distribution and
// use, please see the copyright notice at www.peano-framework.org
//
// peano-minimal: upstream, these helpers forward to exahype2::fv (the Finite
// Volume versions in exahype2/fv/PatchUtils.h). Here they hold the
// implementation themselves, so the Finite Differences do not depend on the
// Finite Volume code. The debug helpers plotPatch(), validatePatch() etc.
// are left out, as nothing in this example calls them.
#pragma once


#include "tarch/Assertions.h"
#include "tarch/la/Vector.h"

#include "peano4/utils/Globals.h"


namespace exahype2 {
  namespace fd {
    /**
     * Size of one grid cell (i.e. one degree of freedom) of a patch
     *
     * The routines are needed within vectorised code. They therefore live in
     * the header, so the compiler can inline them, and are static to avoid
     * multiple symbol errors.
     */
    static tarch::la::Vector<2,double>  getGridCellSize(
      const tarch::la::Vector<2,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis
    )
    {
      tarch::la::Vector<2,double> result;
      for (int d=0; d<2; d++) {
        #if !defined(GPUOffloadingSYCL) and !defined(GPUOffloadingOMP)
        assertion2( numberOfGridCellsPerPatchPerAxis>=1, h, numberOfGridCellsPerPatchPerAxis );
        #endif
        result(d) = h(d)/numberOfGridCellsPerPatchPerAxis;
      }
      return result;
    }


    static tarch::la::Vector<3,double>  getGridCellSize(
      const tarch::la::Vector<3,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis
    )
    {
      tarch::la::Vector<3,double> result;
      for (int d=0; d<3; d++) {
        result(d) = h(d)/numberOfGridCellsPerPatchPerAxis;
      }
      return result;
    }


    static tarch::la::Vector<2,double>  getGridFaceSize(
      const tarch::la::Vector<2,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis
    )
    {
      return getGridCellSize(h,numberOfGridCellsPerPatchPerAxis);
    }


    static tarch::la::Vector<3,double>  getGridFaceSize(
      const tarch::la::Vector<3,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis
    )
    {
      return getGridCellSize(h,numberOfGridCellsPerPatchPerAxis);
    }


    /**
     * Centre of one grid cell of a patch
     *
     * @param x      Centre of the (Peano) cell which hosts the patch
     * @param h      Size of that cell
     * @param index  Index of the grid cell within the patch (lexicographic)
     */
    static tarch::la::Vector<2,double>  getGridCellCentre(
      const tarch::la::Vector<2,double>&  x,
      const tarch::la::Vector<2,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis,
      const tarch::la::Vector<2,int>&     index
    )
    {
      tarch::la::Vector<2,double> cellSize = getGridCellSize(h,numberOfGridCellsPerPatchPerAxis);
      tarch::la::Vector<2,double> result   = x - 0.5 * h + 0.5 * cellSize;
      for (int d=0; d<2; d++) {
        result(d) += index(d) * cellSize(d);
      }
      return result;
    }


    static tarch::la::Vector<3,double>  getGridCellCentre(
      const tarch::la::Vector<3,double>&  x,
      const tarch::la::Vector<3,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis,
      const tarch::la::Vector<3,int>&     index
    )
    {
      tarch::la::Vector<3,double> cellSize = getGridCellSize(h,numberOfGridCellsPerPatchPerAxis);
      tarch::la::Vector<3,double> result   = x - 0.5 * h + 0.5 * cellSize;
      for (int d=0; d<3; d++) {
        result(d) += index(d) * cellSize(d);
      }
      return result;
    }


    /**
     * Centre of one grid cell within the overlap of a face
     *
     * @param overlap Number of grid cell layers per side of the face
     * @param normal  Normal of the face, 0, 1 or 2
     */
    static tarch::la::Vector<2,double>  getGridFaceCentre(
      const tarch::la::Vector<2,double>&  x,
      const tarch::la::Vector<2,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis,
      int                                 overlap,
      int                                 normal,
      const tarch::la::Vector<2,int>&     index
    )
    {
      tarch::la::Vector<2,double> cellSize = getGridFaceSize(h,numberOfGridCellsPerPatchPerAxis);
      tarch::la::Vector<2,double> result;
      for (int d=0; d<2; d++) {
        if (d==normal) {
          result(d) = x(d) - overlap * cellSize(d) + 0.5 * cellSize(d);
        }
        else {
          result(d) = x(d) - 0.5 * h(d) + 0.5 * cellSize(d);
        }
        result(d) += index(d) * cellSize(d);
      }
      return result;
    }


    static tarch::la::Vector<3,double>  getGridFaceCentre(
      const tarch::la::Vector<3,double>&  x,
      const tarch::la::Vector<3,double>&  h,
      int                                 numberOfGridCellsPerPatchPerAxis,
      int                                 overlap,
      int                                 normal,
      const tarch::la::Vector<3,int>&     index
    )
    {
      tarch::la::Vector<3,double> cellSize = getGridCellSize(h,numberOfGridCellsPerPatchPerAxis);
      tarch::la::Vector<3,double> result;
      for (int d=0; d<3; d++) {
        if (d==normal) {
          result(d) = x(d) - overlap * cellSize(d) + 0.5 * cellSize(d);
        }
        else {
          result(d) = x(d) - 0.5 * h(d) + 0.5 * cellSize(d);
        }
        result(d) += index(d) * cellSize(d);
      }
      return result;
    }
  }
}
