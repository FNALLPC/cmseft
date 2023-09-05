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
    argParser.add_argument('--output', action='store', default='./closure.pdf', help="Output file")
    args = argParser.parse_args()

    events_fixed = NanoEventsFactory.from_root(
        'root://cmseos.fnal.gov//store/user/dspitzba/EFT/nanogen_fixed_123.root',
        schemaclass=NanoAODSchema,
    ).events()
    nevents_fixed = len(events_fixed.LHEWeight)


    events_reweighted = NanoEventsFactory.from_root(
        'root://cmseos.fnal.gov//store/user/dspitzba/EFT/nanogen_123.root',
        schemaclass=NanoAODSchema,
    ).events()
    nevents_reweighted = len(events_reweighted.LHEWeight)

    ht_axis = hist.axis.Regular(25, 100, 1500, name="ht", label="HT", underflow=True, overflow=True)

    h_reweighted = hist.Hist(
        ht_axis,
        storage=hist.storage.Weight(),
    )

    h_reweighted.fill(
        ht=ak.sum(events_reweighted.GenJet.pt, axis=1),
        weight=getattr(events_reweighted.LHEWeight, 'EFTrwgt10_ctGRe_2.0_ctGIm_0.0_ctWRe_0.0_ctWIm_0.0_ctBRe_0.0_ctBIm_0.0_cHtbRe_0.0_cHtbIm_0.0_cHt_0.0'),
    )

    h_fixed = hist.Hist(
        ht_axis,
        storage=hist.storage.Weight(),
    )
    h_fixed.fill(
        ht=ak.sum(events_fixed.GenJet.pt, axis=1),
    )

    fig, ax = plt.subplots()

    h_fixed.plot1d(
        ax=ax,
        label=r'$C_{tG}=2 (fixed)$',
        density=True,
    )
    h_reweighted.plot1d(
        ax=ax,
        label=r'$C_{tG}=2 (reweighted)$',
        density=True,
    )

    ax.set_ylabel(r'a.u.')
    ax.set_xlabel(r'$H_{T} (GeV)$')

    ax.set_yscale("log")

    plt.legend()

    fig.savefig(args.output)
    print(f"Figure saved in {args.output}")
