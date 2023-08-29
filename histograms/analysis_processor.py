#!/usr/bin/env python
import numpy as np
import awkward as ak
np.seterr(divide='ignore', invalid='ignore', over='ignore')
from coffea import processor
from coffea.analysis_tools import PackedSelection

# silence warnings due to using NanoGEN instead of full NanoAOD
from coffea.nanoevents import NanoAODSchema
NanoAODSchema.warn_missing_crossrefs = False

import hist
from topcoffea.modules.histEFT import HistEFT

# Get the lumi for the given year
def get_lumi(year):
    lumi_dict = {
        "2016APV": 19.52,
        "2016": 16.81,
        "2017": 41.48,
        "2018": 59.83
    }
    if year not in lumi_dict.keys():
        raise Exception(f"(ERROR: Unknown year \"{year}\".")
    else:
        return(lumi_dict[year])

# Clean objects
def is_clean(obj_A, obj_B, drmin=0.4):
    objB_near, objB_DR = obj_A.nearest(obj_B, return_metric=True)
    mask = ak.fill_none(objB_DR > drmin, True)
    return (mask)

# Main analysis processor
class AnalysisProcessor(processor.ProcessorABC):
    def __init__(self, samples, wc_names_lst=[]):
        self._samples = samples
        self._wc_names_lst = wc_names_lst


        # Create the histograms with new scikit hist
        self._histo_dict = {
            "j0pt": HistEFT(
                hist.axis.StrCategory([], growth=True, name="process"),
                hist.axis.Regular(name="j0pt",label="Leading jet $p_{T}$ (GeV)", bins=10, start=0, stop=600, flow=True),
                wc_names = self._wc_names_lst,
                label="Events",
            ),
            "ht": HistEFT(
                hist.axis.StrCategory([], growth=True, name="process"),
                hist.axis.Regular(name="ht",label="H_T (GeV)", bins=10, start=0, stop=800, flow=True),
                wc_names = self._wc_names_lst,
                label="Events",
            ),
        }


    @property
    def columns(self):
        return self._columns

    def process(self, events):

        # Dataset parameters
        dataset = events.metadata['dataset']
        hist_axis_name = self._samples[dataset]["histAxisName"]
        year   = self._samples[dataset]['year']
        xsec   = self._samples[dataset]['xsec']
        sow    = self._samples[dataset]['nSumOfWeights' ]

        # Extract the EFT quadratic coefficients and optionally use them to calculate the coefficients on the w**2 quartic function
        # eft_coeffs is never Jagged so convert immediately to numpy for ease of use.
        eft_coeffs = ak.to_numpy(events['EFTfitCoefficients']) if hasattr(events, "EFTfitCoefficients") else None

        # Initialize objects
        genpart = events.GenPart
        is_final_mask = genpart.hasFlags(["fromHardProcess","isLastCopy"])
        ele  = genpart[is_final_mask & (abs(genpart.pdgId) == 11)]
        mu   = genpart[is_final_mask & (abs(genpart.pdgId) == 13)]
        jets = events.GenJet


        ######## Lep selection  ########

        e_selec = ((ele.pt>20) & (abs(ele.eta)<2.5))
        m_selec = ((mu.pt>20) & (abs(mu.eta)<2.5))
        leps = ak.concatenate([ele[e_selec],mu[m_selec]],axis=1)


        ######## Jet selection  ########

        jets = jets[(jets.pt>30) & (abs(jets.eta)<2.5)]
        jets_clean = jets[is_clean(jets, leps, drmin=0.4)]
        j0 = jets_clean[ak.argmax(jets.pt,axis=-1,keepdims=True)]


        ######## Event selections ########

        nleps = ak.num(leps)
        njets = ak.num(jets_clean)

        at_least_two_leps = ak.fill_none(nleps>=2,False)
        at_least_two_jets = ak.fill_none(njets>=2,False)

        selections = PackedSelection()
        selections.add('2l2j', at_least_two_leps & at_least_two_jets)


        ######## Normalization ########

        # Normalize by (xsec/sow)
        lumi = 1000.0*get_lumi(year)
        norm = (xsec/sow)*lumi
        wgts = norm*np.ones_like(events['event'])


        ######## Fill histos ########

        hout = self._histo_dict

        variables_to_fill = {
            "j0pt" : j0.pt,
            "ht" : ak.sum(jets.pt,axis=-1),
        }

        event_selection_mask = selections.all("2l2j")

        for var_name, var_values in variables_to_fill.items():

            fill_info = {
                var_name    : var_values[event_selection_mask],
                "process"   : hist_axis_name,
                "weight"    : wgts[event_selection_mask],
                "eft_coeff" : eft_coeffs[event_selection_mask],
            }

            hout[var_name].fill(**fill_info)

        return hout

    def postprocess(self, accumulator):
        return accumulator

