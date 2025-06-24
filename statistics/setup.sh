#!/bin/bash

# Install combine v10.2.1
if [ ! -d CMSSW_14_1_0_pre4 ]; then
    cmsrel CMSSW_14_1_0_pre4

    pushd CMSSW_14_1_0_pre4/src
    cmsenv
    
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    pushd HiggsAnalysis/CombinedLimit
    git fetch origin
    git checkout v10.2.1
    popd

    scramv1 b clean; scramv1 b # always make a clean build
    popd
fi

# ensure environment if running again
pushd CMSSW_14_1_0_pre4/src && cmsenv && popd
