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
and a local copy of `CMSSW_10_6_26` with additional NanoGEN tools to record EFT weights.

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

### Generating EDM GEN files

Producing GEN files from the above gridpack is usually straight forward and similar to other CMS samples.
We will use a fragment file that defines the settings that will be used for decays, parton shower and hadronization in pythia.
For convenience, the gridpack defined in the fragment points to a validated copy at `/eos/uscms/store/user/dspitzba/TT01j_tutorial_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz`.

You can change the path to the gridpack in the file in `cmseft2023/generation/CMSSW_10_6_26/src/Configuration/GenProduction/python/pythia_fragment.py`:

``` python
externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('/eos/uscms/store/user/dspitzba/TT01j_tutorial_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz'),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)
```
If you're not running this tutorial at the LPC you can replace the path to point to your gridpack, or copy the gridpack somewhere convienent using

``` bash
xrdcp root://cmseos.fnal.gov//store/user//dspitzba/TT01j_tutorial_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz /A/B/C
```

For creating a cmsRun config file make sure you are in `cmseft2023/generation/` and have a CMSSW environment set.
``` bash
cmsDriver.py Configuration/GenProduction/python/pythia_fragment.py \
    --mc \
    --python_filename gen_cfg.py \
    --eventcontent RAWSIM,LHE \
    --datatier GEN,LHE \
    --conditions 106X_mc2017_realistic_v6 \
    --beamspot Realistic25ns13TeVEarly2017Collision \
    --step LHE,GEN \
    --nThreads 1 \
    --geometry DB:Extended \
    --era Run2_2017 \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --customise_commands "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=123" \
    --fileout file:gen_123.root \
    --no_exec -n 100
```

To actually create the GEN file just run

``` bash
cmsRun gen_cfg.py
```

<details>
<summary>Using GEN samples to determine the qCut for jet matching</summary>
This is an important topic for any sample that is generated with additional partons in the matrix element, not exclusively for EFT samples.

...
</details>


### Generating NanoGEN files

NanoGEN is a very convenient format for exploratory studies.
The event content of the flat trees is similar to the generator infomration in NanoAOD,
but much faster generation time because the detector simulation and reconstruction is being skipped.

We will generate a few events directly from the gridpack created in the previous step (no intermediate GEN file is needed!), and use the same pythia fragment as in the GEN step before.
Make sure you are in `cmseft2023/generation/` and have a CMSSW environment set.

A cmsRun config file can be created 
``` bash
cmsDriver.py Configuration/GenProduction/python/pythia_fragment.py \
    --python_filename nanogen_cfg.py --eventcontent NANOAODGEN \
    --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAOD \
    --customise_commands "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=123" \
    --fileout file:nanogen_123.root --conditions 106X_mcRun2_asymptotic_v13 \
    --beamspot Realistic25ns13TeV2016Collision --step LHE,GEN,NANOGEN --geometry DB:Extended --era Run2_2016 --no_exec --mc -n 100

```
The CMSSW area that has been set up in the previous step already includes a useful tool that extracts the coefficients of the polynomial fit.
You'll learn more about the coefficients and how to use them in a later part.
Documentation of the used package can be found on the [mgprod github repo](https://github.com/TopEFT/mgprod#additional-notes-on-the-production-of-naod-samples).
If we want to keep the original weights we can add them to the list of named weights in the NanoGEN config file:

``` bash
echo "named_weights = [" >> nanogen_cfg.py
cat TT01j_tutorial_reweight_card.dat | grep launch | sed 's/launch --rwgt_name=/"/' | sed 's/$/",/' >> nanogen_cfg.py
echo -e "]\nprocess.genWeightsTable.namedWeightIDs = named_weights\nprocess.genWeightsTable.namedWeightLabels = named_weights" >> nanogen_cfg.py
```

Producing NanoGEN is fairly fast, and a few thousand events can usually be produced locally like

``` bash
cmsRun nanogen_cfg.py
```

#### Checking the weights

TBD

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

## Statistics

This section of the tutorial will demonstrate how to build a model from the
template histograms and run fits using the
[Combine](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/) tool.

To start, from the main area of this repository, run
```bash
cd statistics
. setup.sh
```
