// This file is part of the Peano project. For conditions of distribution and
// use, please see the copyright notice at www.peano-framework.org
#include "HaloCopy.h"

#include "Enumeration.h"

#include "peano4/utils/Loop.h"
#include "tarch/la/Vector.h"


void toolbox::blockstructured::copyHalfOfHalo(
  int    unknownsPlusAuxiliaryVariables,
  int    numberOfGridCellsPerPatchPerAxis,
  int    haloSize,
  int    normal,
  bool   isRightLayer,
  const double* __restrict__   srcQ,
  double* __restrict__         destQ
) {
  dfore(k,numberOfGridCellsPerPatchPerAxis,normal,0) {
    for (int i= (isRightLayer ? haloSize : 0); i< (isRightLayer ? 2*haloSize : haloSize); i++) {
      tarch::la::Vector<Dimensions,int> overlapCell = k;
      overlapCell(normal) = i;
      const int index = serialiseVoxelIndexInOverlap(overlapCell,numberOfGridCellsPerPatchPerAxis,haloSize,normal);
      for (int j=0; j<unknownsPlusAuxiliaryVariables; j++) {
        destQ[index*unknownsPlusAuxiliaryVariables+j] = srcQ[index*unknownsPlusAuxiliaryVariables+j];
      }
    }
  }
}
