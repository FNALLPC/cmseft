#!/bin/bash

# Install combine v9.2 (min version with interference model)
if [ ! -d CMSSW_11_3_4 ]; then
    cmsrel CMSSW_11_3_4

    pushd CMSSW_11_3_4/src
    cmsenv
    
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    pushd HiggsAnalysis/CombinedLimit
    git fetch origin
    git checkout v9.2.1
    popd
    bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/main/CombineTools/scripts/sparse-checkout-https.sh)

    scramv1 b clean; scramv1 b # always make a clean build
    popd
fi

# ensure environment if running again
pushd CMSSW_11_3_4/src && cmsenv && popd
