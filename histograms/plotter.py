import os
import pickle
import gzip
import matplotlib.pyplot as plt
import topcoffea.modules.utils as utils

import hist
from topcoffea.modules.histEFT import HistEFT

WCPT_EXAMPLES = {
    "nonsm" : {
        "cHtbIm" : 1.5,
        "cHtbRe" : 1.5,
        "ctGIm"  : 1.5, 
        "cHt"    : 1.5, 
        "ctGRe"  : 1.5, 
        "ctWRe"  : 1.5, 
        "ctWIm"  : 1.5, 
        "ctBIm"  : 1.5, 
        "ctBRe"  : 1.5,
    },
    "sm" : {
        "cHtbIm" : 0.0,
        "cHtbRe" : 0.0,
        "ctGIm"  : 0.0, 
        "cHt"    : 0.0, 
        "ctGRe"  : 0.0, 
        "ctWRe"  : 0.0, 
        "ctWIm"  : 0.0, 
        "ctBIm"  : 0.0, 
        "ctBRe"  : 0.0,
    }
}


# Takes a hist with one sparse axis and one dense axis, overlays everything on the sparse axis
def make_single_fig(histo):
    fig, ax = plt.subplots(1, 1, figsize=(7,7))
    histo.plot1d(
        stack=False,
    )
    ax.autoscale(axis='y')
    plt.legend()
    return fig


def main():

    histo_in = "histos_nanogen_small.pkl"

    # Get the histograms
    hin_dict = pickle.load(gzip.open(histo_in))

    # Grab the one we want to plot
    #variable = "j0pt"
    variable = "ht"
    histo = hin_dict[variable]

    # Print values
    print("\nValues:",histo.eval(None))
    print("\nValues EFT:",histo.eval(WCPT_EXAMPLES["nonsm"]))

    # Make plots at a few wc points
    for wcpt_name, wcpt_dict in WCPT_EXAMPLES.items():
        wc_pt = WCPT_EXAMPLES[wcpt_name]
        histo_to_plot = histo.as_hist(wc_pt)
        fig = make_single_fig(histo_to_plot)
        title = f"ttbar_{wcpt_name}.png"
        fig.savefig(os.path.join(".",title))



main()

