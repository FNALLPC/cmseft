#!/bin/bash

# in case this is not already done, setup cms packaging commands
. /cvmfs/cms.cern.ch/cmsset_default.sh

# Install combine v9 + interference PR
# See https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/pull/842 for status
if [ ! -d CMSSW_11_3_4 ]; then
  cmsrel CMSSW_11_3_4
  pushd CMSSW_11_3_4/src
  cmsenv
  git clone -b interference https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
  scram b -j4
  popd
fi

# ensure environment if running again
pushd CMSSW_11_3_4/src && cmsenv && popd
