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
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
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
We will start by creating a gridpack. Start in a fresh terminal window.

Find the files under `genproductions/bin/MadGraph5_aMCatNLO`, Take a look at gridpack_generation.sh. Add a new model SMEFTsim_topU3l_MwScheme 
```bash
cp diagram_generation.sh genproductions/bin/MadGraph5_aMCatNLO/
cd genproductions/bin/MadGraph5_aMCatNLO/
mkdir -pv addons/models/
wget https://feynrules.irmp.ucl.ac.be/raw-attachment/wiki/SMEFT/SMEFTsim_topU3l_MwScheme_UFO.tar.gz
tar -xvzf SMEFTsim_topU3l_MwScheme_UFO.tar.gz
cd SMEFTsim_topU3l_MwScheme_UFO
```

Create a folder “TT01j_tutorial”
Take a look at TT01j_tutorial_proc_card.dat and TT01j_tutorial_reweight_card.dat
```bash
mkdir TT01j_tutorial
cp ../../../../../../../TT01j* .
cd addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial
```
Let's take a look at some diagrams
```bash
 cd ../../../../
 ./diagram_generation.sh TT01j_tutorial addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial/
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

### Running the processor
Run the processor over the example root file.
```
python run_processor.py example_sample.json
```

### Other things to try

You can try exploring the quadratic parameterization with `get_quad_coeff.py`. This script explores some of the contents of the nanogen root file. The script will open the file, extract the WC quadratic fit coefficients for each event and sum them (so we are just looking at inclusive parametrization). It will then the quadratic fit coefficients into a json that you can take a look at. It will also make some simple 1d plots of the 1d slices of the n-dimensional quadratic parameterization. 
```
python get_quad_coeff.py nanogen_small.root
```

To explore the output histogram (from the running the processor step), you can take a look at the resulting histograms and try to reweight to a non-SM point to see how it compares to the shape and normalization at the SM. E.g.:
```
python plotter.py histos.pkl.gz
```

### Saving templates for use with combine
Before going to the next section, run
```bash
./dump_templates.py histos.pkl.gz
```
which will write two files into `../statistics/` directory for use with the next section.

## Statistics

This section of the tutorial will demonstrate how to build a model from the
template histograms and run fits using the
[Combine](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/) tool.

To start, from the main area of this repository, run
```bash
cd statistics
. setup.sh
```

### Creating a workspace with per-bin morphing

Run
```bash
text2workspace.py signal_region_card.txt --X-allow-no-background -P HiggsAnalysis.CombinedLimit.InterferenceModels:interferenceModel \
  --PO verbose --PO scalingData=scaling.pkl.gz -o workspace.root
```

### Running fits and scans
```
combine -M MultiDimFit workspace.root --freezeParameters cHtbIm,cHtbRe,ctGIm,ctWRe,ctWIm,ctBIm,ctBRe \
  --redefineSignalPOIs cHt,ctGRe --setParameters cHt=0,ctGRe=0 --algo singles
```

Do some scans too...

### PCA
Run
```bash
combine -M MultiDimFit workspace.root --skipInitialFit --robustHesse 1
```
which computes the Hessian of the likelihood at the initial point. Since we have an Asimov dataset, this
initial point should be a global minimum, and we can use it to understand what, if any, degeneracies in the parameters
exist at this point. The command will output a file we can look at
```
$ root -l robustHesseTest.root
root [0]
Attaching file robustHesseTest.root as _file0...
(TFile *) 0x4716940
root [1] TMatrixDSymEigen eig(*hessian);
root [2] eig.GetEigenValues().Print()

Vector (16)  is as follows

     |        1  |
------------------
   0 |0.838318
   1 |0.573909
   2 |0.380058
   3 |0.263561
   4 |0.221969
   5 |0.19812
   6 |0.196478
   7 |0.195322
   8 |0.0850279
   9 |0.0776739
  10 |0.0650077
  11 |0.040883
  12 |0.0227485
  13 |0.00564541
  14 |0.00187942
  15 |0.00125546
```
but this includes both the POIs as well as the BB-lite nuisance parameters. We need to get the _profile hessian_ to know what the POIs constraint is.
