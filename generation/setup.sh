#!/bin/bash

if [ ! -d genproductions ]; then
  git clone https://github.com/cms-sw/genproductions -b mg265UL
fi

# in case this is not already done, setup cms packaging commands
. /cvmfs/cms.cern.ch/cmsset_default.sh

if [ ! -d CMSSW_10_6_26 ]; then
  cmsrel CMSSW_10_6_26
  pushd CMSSW_10_6_26/src
  export SCRAM_ARCH=slc7_amd64_gcc700
  cmsenv
  git cms-init

  git cms-addpkg PhysicsTools/NanoAOD
  cd PhysicsTools/NanoAOD/
  git remote add eftfit https://github.com/GonzalezFJR/cmssw.git
  git fetch eftfit
  git cherry-pick c0901cfc459a8d5282ebb1bc74374903d29e3eee
  git cherry-pick 4068e48b02b1fcb46949b3ebeac6a7b59062c2e0
  git cherry-pick 76d0a24615c2b2b3aa7333c5aed5cc7bb6a7fd1d

  cd ../../
  git clone https://github.com/TopEFT/EFTGenReader.git

  mkdir -p Configuration/GenProduction/python/
  cp ../../fragments/pythia_fragment.py Configuration/GenProduction/python/

  scram b -j 4
  popd
fi

# ensure environment if running again
pushd CMSSW_10_6_26/src && cmsenv && popd


cmsDriver.py Configuration/GenProduction/python/pythia_fragment.py \
    --python_filename nanogen_cfg.py --eventcontent NANOAODGEN \
    --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAOD \
    --customise_commands "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=123" \
    --fileout file:nanogen_123.root --conditions 106X_mcRun2_asymptotic_v13 \
    --beamspot Realistic25ns13TeV2016Collision --step LHE,GEN,NANOGEN --geometry DB:Extended --era Run2_2016 --no_exec --mc -n 10


echo "named_weights = [" >> nanogen_cfg.py
cat TT01j_tutorial_reweight_card.dat | grep launch | sed 's/launch --rwgt_name=/"/' | sed 's/$/",/' >> nanogen_cfg.py
echo -e "]\nprocess.genWeightsTable.namedWeightIDs = named_weights\nprocess.genWeightsTable.namedWeightLabels = named_weights" >> nanogen_cfg.py
