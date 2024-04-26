#!/bin/bash

if [ ! -d genproductions ]; then
  git clone https://github.com/danbarto/genproductions -b fix_patching --depth 1
fi

# in case this is not already done, setup cms packaging commands
. /cvmfs/cms.cern.ch/cmsset_default.sh
 export SCRAM_ARCH=el8_amd64_gcc11
if [ ! -d CMSSW_13_0_14 ]; then
  cmsrel CMSSW_13_0_14
  pushd CMSSW_13_0_14/src
  export SCRAM_ARCH=el8_amd64_gcc11
  cmsenv
  git cms-init

  git cms-addpkg PhysicsTools/NanoAOD
  cd PhysicsTools/NanoAOD/
  git remote add eftfit https://github.com/danbarto/cmssw.git
  git fetch eftfit

  # these might not work yet
  git cherry-pick ffba2640cf7d8da6b8b36559c64e90a2076153e9
  git cherry-pick 416096620ec9d477caad74704c40d3d7d695e06a
  git cherry-pick f9a76b864ebf40833f73b03778634b553aecfc98
  git cherry-pick 48581ffb94b1957203160428745b69048a7ffc94

  cd ../../
  git clone https://github.com/danbarto/EFTGenReader.git

  mkdir -p Configuration/GenProduction/python/
  cp ../../fragments/pythia_fragment.py Configuration/GenProduction/python/

  scram b -j 4
  popd
fi

# ensure environment if running again
pushd CMSSW_13_0_14/src && cmsenv && popd
