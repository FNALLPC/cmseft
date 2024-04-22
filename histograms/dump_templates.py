#!/usr/bin/env python3
import os
import pickle
import gzip
import argparse

import numpy as np
import uproot


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_histo_file")
    args = parser.parse_args()

    with gzip.open(args.input_histo_file) as fin:
        histos = pickle.load(fin)


    hthist = histos["ht"]
    print(f"Using {hthist} to build templates")

    # isolate signal and skip first two bins (empty due to ht cut)
    httbar = hthist["ttbar", 2:, :]

    # templates at wc=0
    with uproot.recreate("templates.root") as fout:
        fout["ttbar"] = httbar.as_hist({})
        # fake data
        fout["data_obs"] = httbar.as_hist({})

    # scaling relative to nominal
    nparam = 1 + len(httbar.wc_names)
    # HistEFT stores scaling in same format as combine expects
    # but the off-diagonal elements are twice as large
    prefactor = 0.5*(np.ones((nparam, nparam)) + np.eye(nparam))[np.tril_indices(nparam)]
    scaling = [
        {
            "channel": "SR",
            "process": "ttbar",
            "parameters": ["cSM[1]"] + [f"{wc}[0,-50,50]" for wc in httbar.wc_names],
            # make a contiguous copy to ensure it is as small as possible
            # normalize to the SM yield
            "scaling": np.ascontiguousarray(httbar.values() * prefactor / httbar.values()[:, 0, None]),
        },
    ]
    print(scaling)
    with gzip.open("scaling.pkl.gz", "wb") as fout:
        pickle.dump(scaling, fout)
