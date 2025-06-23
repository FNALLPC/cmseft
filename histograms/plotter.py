import os
import pickle
import gzip
import argparse
import matplotlib.pyplot as plt
import topcoffea.modules.utils as utils

import hist
from topcoffea.modules.histEFT import HistEFT

WCPT_EXAMPLES = {
    "sm" : {
        "ctWRe" : 0.0,
        "ctGRe" : 0.0,
        "ctj8"  : 0.0,
        "ctq1"  : 0.0,
        "ctu1"  : 0.0,
    },
    "non_sm_point_1" : {
        "ctWRe" : 0.0,
        "ctGRe" : 0.0,
        "ctj8"  : 1.5,
        "ctq1"  : 0.0,
        "ctu1"  : 0.0,
    },
    "non_sm_point_2" : {
        "ctWRe" : 1.5,
        "ctGRe" : 1.5,
        "ctj8"  : 1.5,
        "ctq1"  : 1.5,
        "ctu1"  : 1.5,
    },
}


# Takes a hist with one sparse axis and one dense axis, overlays everything on the sparse axis
def make_single_fig(histo, wc_points_to_plot):
    fig, ax = plt.subplots(1, 1, figsize=(7,7))

    for wc_pt_name, wc_pt_vals in wc_points_to_plot.items():
        histo_to_plot = histo.as_hist(wc_pt_vals)
        histo_to_plot.plot1d(
            stack=False,
            label=wc_pt_name,
        )
    ax.autoscale(axis='y')
    plt.legend()
    return fig


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("input_histo_file")
    args = parser.parse_args()

    histo_in = args.input_histo_file

    # Get the histograms
    hin_dict = pickle.load(gzip.open(histo_in))

    # Grab the one we want to plot
    #variable = "j0pt"
    variable = "ht"
    histo = hin_dict[variable]

    # Print some values to see how they differ at the SM and a non-SM point
    print(f"\nValues at SM: \n{histo.eval(None)}")
    print(f"\nValues a non-SM point: \n{histo.eval(WCPT_EXAMPLES['non_sm_point_2'])}")

    # Make plots at a few wc points
    print(f"\nPlotting..")
    fig = make_single_fig(
        histo,
        wc_points_to_plot = WCPT_EXAMPLES,
    )
    title = f"ttbar_{variable}.png"
    fig.savefig(os.path.join(".",title))
    print(f"Saved as \"{title}\"")



main()

