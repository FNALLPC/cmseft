#!/bin/bash

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
unset PYTHONPATH # To avoid conflicts 
JHUGENFOLDER="JHUGenerator.v7.5.7"

curdir=$PWD

if [ -d "CMSSW_14_0_0" ]; then
    echo "CMSSW_14_0_0 already exists!"
else
    cmsrel CMSSW_14_0_0
fi

cd CMSSW_14_0_0/src
cmsenv

if [ -d ${JHUGENFOLDER} ]; then
    echo "${JHUGENFOLDER} already exists!"
else
    wget "https://spin.pha.jhu.edu/Generator/${JHUGENFOLDER}.tar.gz"
    tar -xvf "${JHUGENFOLDER}.tar.gz"
fi

cd "${JHUGENFOLDER}/JHUGenMELA/MELA/"
sed -i '23s/slc7_amd64_gcc920/el9_amd64_gcc12/' setup.sh

./setup.sh
eval $(./setup.sh env standalone)

cd ../../JHUGenLexicon
make

cd $curdir
