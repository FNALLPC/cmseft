#!/bin/bash

if [ ! -d genproductions ]; then
  git clone https://github.com/cms-sw/genproductions -b mg265UL
fi

# in case this is not already done, setup cms packaging commands
. /cvmfs/cms.cern.ch/cmsset_default.sh

if [ ! -d CMSSW_10_6_27 ]; then
  cmsrel CMSSW_10_6_27
  pushd CMSSW_10_6_27/src
  cmsenv
  git cms-init
  # git cms-addpkg PhysicsTools/NanoAOD
  # setup weights table producer
  # scram b -j4
  popd
fi

# ensure environment if running again
pushd CMSSW_10_6_27/src && cmsenv && popd
