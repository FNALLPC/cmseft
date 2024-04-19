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
git clone git@github.com:FNALLPC/cmseft.git
```

## Generation

The first section of the tutorial will discuss generating samples of events
with [Madgraph](https://launchpad.net/mg5amcnlo) and
[SMEFTsim](https://smeftsim.github.io/), with weights embedded per-event to
allow reweighting the samples to alternative points in EFT coefficient space.
For this exercise we will generate a $t\bar{t}$ semileptonic sample with one extra jet. 

To start, from the main area of this repository, run
```bash
cd cmseft/generation
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

The gridpack generation in this tutorial runs on scl7/centos7. We will therefore run in a singularity container.
On the LPC:

``` bash
cmssw-cc7 --bind `readlink -f ${HOME}/nobackup/` --bind /cvmfs
```
On lxplus

``` bash
cmssw-cc7 --bind /cvmfs
```
Now, navigate back to your EFT tutorial work directory.

Find the files under `genproductions/bin/MadGraph5_aMCatNLO`, Take a look at gridpack_generation.sh. Add a new model SMEFTsim_topU3l_MwScheme 
```bash
export TUTORIALGEN=$(pwd) 
cp diagram_generation.sh genproductions/bin/MadGraph5_aMCatNLO/
cd genproductions/bin/MadGraph5_aMCatNLO/
mkdir -pv addons/models/
cd addons/models/
wget https://feynrules.irmp.ucl.ac.be/raw-attachment/wiki/SMEFT/SMEFTsim_topU3l_MwScheme_UFO.tar.gz
tar -xvzf SMEFTsim_topU3l_MwScheme_UFO.tar.gz
cd SMEFTsim_topU3l_MwScheme_UFO
```

Create a folder “TT01j_tutorial”
Take a look at TT01j_tutorial_proc_card.dat and TT01j_tutorial_reweight_card.dat
```bash
mkdir TT01j_tutorial
cp $TUTORIALGEN/TT01j* TT01j_tutorial/
```
Let's take a look at some diagrams
```bash
 cd $TUTORIALGEN/genproductions/bin/MadGraph5_aMCatNLO/
 eval `scram unsetenv -sh`
 ./diagram_generation.sh TT01j_tutorial addons/models/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial/
```

To run locally,
```bash
./gridpack_generation.sh TT01j_tutorial addons/models/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial
```

<details>
<summary>Alternative: run on condor</summary>
Condor gridpack generation works for lxplus (and LPC?) but may not work at your local cluster, depending on your cluster's batch setup. You could use CMS connect as well (link)
  
```bash
nohup ./submit_cmsconnect_gridpack_generation.sh TT01j_tutorial addons/cards/SMEFTsim_topU3l_MwScheme_UFO/TT01j_tutorial > TT01j_tutorial.log
```
</details>

### Generating EDM GEN files

Exit the singularity container from the previous step. If you're running on an EL8 machine (e.g. `lxplus8.cern.ch` or `cmslpc-el8.fnal.gov`) you can run the following commands without a container.
Navigate back to your EFT tutorial work directory.

``` bash
cd generation/
pushd CMSSW_13_0_14/src && cmsenv && popd
```

Producing GEN files from the above gridpack is usually straight forward and similar to other CMS samples.
We will use a fragment file that defines the settings that will be used for decays, parton shower and hadronization in pythia.
For convenience, the gridpack defined in the fragment points to a validated copy at `/eos/uscms/store/user/dspitzba/TT01j_tutorial_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz`.

You can change the path to the gridpack in the file in `cmseft/generation/CMSSW_10_6_26/src/Configuration/GenProduction/python/pythia_fragment.py`:

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
    --conditions 130X_mcRun3_2023_realistic_v14 \
    --beamspot Realistic25ns13p6TeVEarly2023Collision \
    --step LHE,GEN \
    --nThreads 1 \
    --geometry DB:Extended \
    --era Run3 \
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
The qCut is set in the pythia fragment.
A good starting point is around the xqcut that is being set in the MG run_card.dat.

Several GEN files with different qcut values have been prepared in `/eos/uscms/store/user/dspitzba/EFT/qcut*.root*`.
You can look them up from anywhere with a grid certificate with

``` bash
xrdfs root://cmseos.fnal.gov/ ls /store/user/dspitzba/EFT/
```

You can plot differential jet rate plots:

``` bash
. setup_hist.sh
python djr.py --input root://cmseos.fnal.gov//store/user/dspitzba/EFT/qcut30.root --output djr_qcut30.pdf
```

</details>


### Generating NanoGEN files

NanoGEN is a very convenient format for exploratory studies.
The event content of the flat trees is similar to the generator infomration in NanoAOD,
but much faster generation time because the detector simulation and reconstruction is being skipped.

We will generate a few events directly from the gridpack created in the previous step (no intermediate GEN file is needed!), and use the same pythia fragment as in the GEN step before.
Make sure you are in `cmseft2023/generation/` and have a CMSSW environment set (e.g. run `. setup.sh` again to be sure).

A cmsRun config file can be created 

``` bash
cmsDriver.py Configuration/GenProduction/python/pythia_fragment.py \
    --python_filename nanogen_cfg.py --eventcontent NANOAODGEN \
    --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAOD \
    --customise_commands "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=123" \
    --fileout file:nanogen_123.root --conditions 130X_mcRun3_2023_realistic_v14 --beamspot Realistic25ns13p6TeVEarly2023Collision \
    --step LHE,GEN,NANOGEN --geometry DB:Extended --era Run3 --no_exec --mc -n 100

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

It is always a good idea to check if some of the weights have enhanced tails.
A simple script that reads the weights and makes a histogram for the pure `ctG` contributions can be run with

``` bash
. setup_hist.sh
python weights.py
```

Additionally, it is always a good idea to compare a reweighted sample with a sample that has been produced at a fixed EFT point.

``` bash
python closure.py
```

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

This section will be run outside of the conda enviornment used so far. To exit the environment, run
```
conda deactivate
```

To start, from the main area of this repository, run
```bash
cd statistics
. setup.sh
```

### Creating a workspace with process scaling
Run
```bash
PYTHONPATH=$PWD:$PYTHONPATH text2workspace.py signal_region_card.txt --X-allow-no-background -P eftmodel:eftModel -o workspace_norm.root
```
(we're abusing the python path a bit but the model object is only needed during this step)

### Creating a workspace with per-bin morphing

Run
```bash
text2workspace.py signal_region_card.txt --X-allow-no-background -P HiggsAnalysis.CombinedLimit.InterferenceModels:interferenceModel \
  --PO verbose --PO scalingData=scaling.pkl.gz -o workspace.root
```
which implements the [interferenceModel](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/interference/docs/part2/physicsmodels.md#multi-process-interference)
physics model in combine using the scaling data constructed at the end of the previous section.

### Running fits and scans
```
combine -M MultiDimFit workspace.root --freezeParameters cHtbIm,cHtbRe,ctGIm,ctWRe,ctWIm,ctBIm,ctBRe \
  --redefineSignalPOIs cHt,ctGRe --setParameters cHt=0,ctGRe=0 --algo singles
```

To perform a one-dimensional likelihood scan on cHt (freezing all other WC to 0), run
```
combineTool.py workspace.root -M MultiDimFit --algo grid --points 10 \
    --freezeParameters cHtbIm,cHtbRe,ctGIm,ctWRe,ctWIm,ctBIm,ctBRe,ctGRe \
    --redefineSignalPOIs cHt -n Scan1D.cHt
```
To plot the likelihood scan, run
```
python plot1d.py -p cHt
```
An analogous set of commands can be used to generate 1D likelihood scans of the other WC.

To perform a two-dimensional likelihood scan on cHt and ctGRe (freezing all other WC to 0), run
```
combineTool.py workspace.root -M MultiDimFit --algo grid --points 100 \
    --freezeParameters cHtbIm,cHtbRe,ctGIm,ctWRe,ctWIm,ctBIm,ctBRe \
    --redefineSignalPOIs cHt,ctGRe -n Scan2D.cHt.ctGRe
```
To plot the 2D likelihood scan, run
```
python plot2d.py -p cHt,ctGRe
```
Again, analogous commands can be used to generate the 2D likelihood scan for other combinations of WC.

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
