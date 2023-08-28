# CMS EFT Workshop Hands-on tutorial

This is a companion repository for CMS EFT workshop at LPC tutorial.
The tutorial is aimed at graduate students and other researchers who are interested in including an EFT interpretation in their analysis.

## Setup

All necessary ingredients are either included as part of this repository or
available on `/cvmfs`.  Please feel free to use your favorite computing cluster
interactive machine, e.g. [FNAL LPC](https://uscms.org/uscms_at_work/physics/computing/getstarted/uaf.shtml),
[LXplus](https://abpcomputing.web.cern.ch/computing_resources/lxplus/), etc.

To start, please clone this repository in a directory that has sufficient quota for the tutorial (at least 50GB),
```bash
git clone git@github.com:FNALLPC/cmseft2023.git
```

## Generation

The first section of the tutorial will discuss generating samples of events
with [Madgraph](https://launchpad.net/mg5amcnlo) and
[SMEFTsim](https://smeftsim.github.io/), with weights embedded per-event to
allow reweighting the samples to alternative points in EFT coefficient space.
For this exercise we will generate a $t\bar{t}$ semileptonic sample with one extra jet. 

To start, from the main area of this repository, run
```bash
voms-proxy-init -voms cms -valid 192:00
cd generation
. setup.sh
```
this sets up the CMS [genproductions](https://github.com/cms-sw/genproductions) git repository
and a local copy of `CMSSW_10_6_27` with additional NanoGEN tools to record EFT weights.

<details>
<summary>Alternative: setup without CMSSW, using LCG</summary>
LCG stack with MG+Pythia+Delphes
</details>

<details>
<summary>Alternative: other UFO models for EFT parameterization</summary>
Alternative generators include SMEFT@NLO, Dim6Top, etc.
  These can be installed using...
</details>

### Creating the gridpack
We will start by creating a gridpack

Find the files under `genproductions/bin/MadGraph5_aMCatNLO`, Take a look at gridpack_generation.sh. Add a new model SMEFTsim_topU3l_MwScheme 
```bash
mkdir -pv addons/models/SMEFTsim_topU3l_MwScheme_UFO
cd addons/models/SMEFTsim_topU3l_MwScheme_UFO
```

Add all files from https://github.com/HephyAnalysisSW/genproductions/tree/mg265UL/bin/MadGraph5_aMCatNLO/addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial under a folder “TT01j_tutorial”
Take a look at TT01j_tutorial_proc_card.dat and TT01j_tutorial_reweight_card.dat
```bash
cd addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial
```
To run locally,
```bash
./gridpack_generation.sh TT01j_tutorial addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial
```

<details>
<summary>Alternative: run on condor</summary>
Condor gridpack generation works for lxplus (and LPC?) but may not work at your local cluster, depending on your cluster's batch setup. You could use CMS connect as well (link)
```bash
nohup ./submit_cmsconnect_gridpack_generation.sh TT01j_tutorial addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial > TT01j_tutorial.log
```
</details>

## Histograms

This section of the tutorial will detail how to take the EFT-weighted events
and make selections and store EFT-aware histograms.

To start, from the main area of this repository, run
```bash
cd histograms
. setup.sh
```

## Statistics

This section of the tutorial will demonstrate how to build a model from the
template histograms and run fits using the
[Combine](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/) tool.

To start, from the main area of this repository, run
```bash
cd statistics
. setup.sh
```
