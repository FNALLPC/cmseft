#!/bin/bash

if [ ! -d genproductions ]; then
  git clone https://github.com/cms-sw/genproductions.git --depth 1
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
  git remote add eftfit https://github.com/bryates/cmssw.git
  git fetch eftfit
  git cherry-pick 869fdb3011b1d864d3d85090ee4e22ea3fdb32f9
  git cherry-pick 493da24362983cb78b0e9ad75f3cc6d824b54f5e
  git cherry-pick 10e20e3b235870519b870e3c3cfb13f9b23148e2
  git cherry-pick bb9ab6f1b1cf5e786437f3d2e482bf50404e0d50

  cd ../../
  git clone https://github.com/TopEFT/EFTGenReader.git
  rm -rf EFTGenReader/GenReader/
  rm -rf EFTGenReader/LHEReader/

  mkdir -p Configuration/GenProduction/python/
  cp ../../fragments/pythia_fragment.py Configuration/GenProduction/python/

  scram b -j 4
  popd
fi

# ensure environment if running again
pushd CMSSW_13_0_14/src && cmsenv && popd
