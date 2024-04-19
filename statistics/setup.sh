#!/bin/bash

# Install combine v9 + interference PR
# See https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/pull/842 for status
if [ ! -d CMSSW_11_3_4 ]; then
    cmsrel CMSSW_11_3_4

    pushd CMSSW_11_3_4/src
    cmsenv
    
    git clone -b interference https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/main/CombineTools/scripts/sparse-checkout-https.sh)

    scramv1 b clean; scramv1 b # always make a clean build
    popd
fi

# ensure environment if running again
pushd CMSSW_11_3_4/src && cmsenv && popd
