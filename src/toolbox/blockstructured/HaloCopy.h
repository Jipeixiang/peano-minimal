// This file is part of the Peano project. For conditions of distribution and
// use, please see the copyright notice at www.peano-framework.org
//
// peano-minimal: moved here from exahype2/fv/PatchUtils.h. The copy does not
// depend on the discretisation, and the fourth-order Finite Differences use
// it as well, so it belongs to the block-structured toolbox rather than to
// the Finite Volume namespace.
#pragma once


namespace toolbox {
  namespace blockstructured {
    /**
     * Copy one half of a face overlap
     *
     * A face always holds a left and a right overlap, i.e. haloSize layers of
     * grid cells from each of the two adjacent patches. The overlap is stored
     * as AoS and enumerated via serialiseVoxelIndexInOverlap(). This routine
     * copies the left (isRightLayer=false) or right (isRightLayer=true) half
     * from srcQ to destQ.
     *
     * @param unknownsPlusAuxiliaryVariables Entries per grid cell
     * @param numberOfGridCellsPerPatchPerAxis Patch size
     * @param haloSize Number of grid cell layers per half, i.e. the overlap
     * @param normal Normal of the face, 0, 1 or 2
     */
    void copyHalfOfHalo(
      int    unknownsPlusAuxiliaryVariables,
      int    numberOfGridCellsPerPatchPerAxis,
      int    haloSize,
      int    normal,
      bool   isRightLayer,
      const double* __restrict__   srcQ,
      double* __restrict__         destQ
    );
  }
}
