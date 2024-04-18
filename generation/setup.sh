#!/bin/bash

if [ ! -d genproductions ]; then
  git clone https://github.com/cms-sw/genproductions -b master --depth 1
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
  git cherry-pick c0901cfc459a8d5282ebb1bc74374903d29e3eee
  git cherry-pick 4068e48b02b1fcb46949b3ebeac6a7b59062c2e0
  git cherry-pick 76d0a24615c2b2b3aa7333c5aed5cc7bb6a7fd1d
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
