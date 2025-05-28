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
        'root://cmseos.fnal.gov//store/user/byates1/EFT/nanogen_fixed_123.root',
        schemaclass=NanoAODSchema,
    ).events()
    nevents_fixed = len(events_fixed.LHEWeight)


    events_reweighted = NanoEventsFactory.from_root(
        'root://cmseos.fnal.gov//store/user/byates1/EFT/nanogen_123.root',
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
        # NOTE We're filling with the actual MG weights so the error bars _will_ be correct in this case
        weight=getattr(events_reweighted.LHEWeight, 'EFTrwgt10_ctGRe_2.0_ctGIm_0.0_ctWRe_0.0_ctWIm_0.0_ctBRe_0.0_ctBIm_0.0_cHtbRe_0.0_cHtbIm_0.0_cHt_0.0'),
    )

    h_fixed = hist.Hist(
        ht_axis,
        storage=hist.storage.Weight(),
    )
    h_fixed.fill(
        ht=ak.sum(events_fixed.GenJet.pt, axis=1),
    )

    fig, (ax, rax) = plt.subplots(
            nrows=2,
            ncols=1,
            gridspec_kw={"height_ratios": (3, 1)},
            sharex=True
    )
    plt.sca(ax)
    # Using the Run 3 COM and 2023 lumi
    hep.cms.label(label='', lumi='32.7', data=False, com=13.6)

    h_fixed.plot1d(
        ax=ax,
        label=r'$C_{tG}=2 (fixed)$',
        density=True,
    )
    hep.histplot(h_reweighted,
        ax=ax,
        label=r'$C_{tG}=2 (reweighted)$',
        density=True,
        #yerr=False # NOTE be careful here, error bars on reweighted samples are not always accurate
                    # (e.g., if you're using something like `histEFT` where the bin yields are computed on the fly)
    )
    hep.histplot(
            h_fixed.values() / h_fixed.values(),
            bins=h_reweighted.axes[-1].edges,
            yerr=(np.sqrt(h_fixed.variances()) / h_fixed.values()),
            ax=rax)
    hep.histplot(
            h_reweighted.values() / h_fixed.values() * np.sum(h_fixed.values())/np.sum(h_reweighted.values()),
            bins=h_reweighted.axes[-1].edges,
            ax=rax)

    ax.set_ylabel(r'a.u.')
    ax.set_xlabel(r'$H_{T} (GeV)$')
    rax.set_ylabel(r'Ratio (shape)')
    rax.set_ylim(0.5, 1.5)

    ax.set_yscale("log")

    plt.legend()

    fig.savefig(args.output)
    print(f"Figure saved in {args.output}")
