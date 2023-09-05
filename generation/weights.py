#!/usr/bin/env python3

import uproot
import hist
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import warnings
plt.style.use(hep.style.CMS)

NanoAODSchema.warn_missing_crossrefs = False

if __name__ == '__main__':

    import argparse

    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--input', action='store', default='root://cmseos.fnal.gov//store/user/dspitzba/EFT/nanogen_small.root', help="Input file")
    argParser.add_argument('--output', action='store', default='./weights.pdf', help="Output file")
    args = argParser.parse_args()

    events = NanoEventsFactory.from_root(
        args.input,
        schemaclass=NanoAODSchema,
    ).events()

    w = events.LHEWeight
    eft_weight_names = [ x for x in w.fields if x.startswith('EFT') ]

    weight_axis = hist.axis.Regular(50, -1, 5, name="weight_ax", label="weight", underflow=True, overflow=True)

    h_SM = hist.Hist(weight_axis)
    h_SM.fill(weight_ax=getattr(events.LHEWeight, eft_weight_names[0]))

    h_ctg1 = hist.Hist(weight_axis)
    h_ctg1.fill(weight_ax=getattr(events.LHEWeight, 'EFTrwgt1_ctGRe_1.0_ctGIm_0.0_ctWRe_0.0_ctWIm_0.0_ctBRe_0.0_ctBIm_0.0_cHtbRe_0.0_cHtbIm_0.0_cHt_0.0'))

    # EFTrwgt10_ctGRe_2.0_ctGIm_0.0_ctWRe_0.0_ctWIm_0.0_ctBRe_0.0_ctBIm_0.0_cHtbRe_0.0_cHtbIm_0.0_cHt_0.0
    h_ctg2 = hist.Hist(weight_axis)
    h_ctg2.fill(weight_ax=getattr(events.LHEWeight, 'EFTrwgt10_ctGRe_2.0_ctGIm_0.0_ctWRe_0.0_ctWIm_0.0_ctBRe_0.0_ctBIm_0.0_cHtbRe_0.0_cHtbIm_0.0_cHt_0.0'))


    fig, ax = plt.subplots()

    h_SM.plot1d(ax=ax, label=r'$C_{tG}=0$')
    h_ctg1.plot1d(ax=ax, label=r'$C_{tG}=1$')
    h_ctg2.plot1d(ax=ax, label=r'$C_{tG}=2$')

    ax.set_ylabel(r'# Events')
    ax.set_xlabel(r'weight')

    ax.set_yscale("log")

    plt.legend()

    fig.savefig(args.output)
    print(f"Figure saved in {args.output}")

