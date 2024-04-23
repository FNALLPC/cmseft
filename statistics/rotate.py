import argparse
import gzip
import pickle
import re

import numpy as np
import ROOT
from HiggsAnalysis.CombinedLimit.InterferenceModels import read_scaling

def _tmatrix2numpy(mat):
    out = np.empty(shape=(mat.GetNrows(), mat.GetNcols()))
    for i, j in np.ndindex(out.shape):
        out[i, j] = mat[i][j]
    return out

def _profile_hessian(hess, isPoi):
    """Compute the profile hessian for a given set of parameters of interest (POI)

    hess: (n,n) numpy array of doubles
    isPoi: (n,) numpy array of bools indicating position in row/column of POI variables

    The profile hessian can be found from the inverse of the POI submatrix of
    the covariance matrix, which is the inverse hessian. But if the hessian is
    singular, we can't invert it! We can nevertheless compute the profile
    hessian if the nuisance parameter submatrix is invertible using the Schur
    complement: https://en.wikipedia.org/wiki/Schur_complement
    """
    poi_poi = hess[isPoi, :][:, isPoi]
    poi_np = hess[isPoi, :][:, ~isPoi]
    np_np = hess[~isPoi, :][:, ~isPoi]
    return poi_poi - poi_np @ np.linalg.inv(np_np) @ poi_np.T


def _tril_to_square(scaling, npar):
    nbin, ntril = scaling.shape
    assert ntril == npar*(npar+1)//2
    out = np.zeros((nbin, npar, npar))
    for i, tril in enumerate(scaling):
        square = np.zeros((npar, npar))
        js, ks = np.tril_indices(npar)
        out[i, js, ks] = tril
        out[i, ks, js] = tril
    return out

def _square_to_tril(scaling):
    nbin, npar, _ = scaling.shape
    ntril = npar*(npar+1)//2
    out = np.zeros((nbin, ntril))
    for i, square in enumerate(scaling):
        out[i, :] = square[np.tril_indices(npar)]
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate scaling data based on robustHesse output")
    parser.add_argument('--hesse', required=True, help="RobustHesse output file")
    parser.add_argument('--scalingIn', required=True, help = 'Original scaling data JSON/pickle file')
    parser.add_argument('--scalingOut', default="rotated_scaling.pkl.gz", help = 'Updated scaling data output (gzip-pickle only)')
    parser.add_argument('--scaleByEigenvalue', action="store_true", help="Scale the eigenvectors by their eigenvalue")
    parser.add_argument('--threshold', default=1/25.0, help="Eigenvalue threhold for hessian (1/sqrt(threshold) for uncertainty)")
    args = parser.parse_args()

    fin = ROOT.TFile.Open(args.hesse)
    params = list(fin.Get("floatParsFinal"))
    isPoi = np.array(["group_POI" in p.attributes() for p in params])
    poinames = [p.GetName() for p, i in zip(params, isPoi) if i]
    print(f"Found {isPoi.sum()} POIs: {poinames}")

    hess = _tmatrix2numpy(fin.Get("hessian"))
    feig, _ = np.linalg.eigh(hess)
    print(f"Full hessian eigenvalues: {feig}")

    phess = _profile_hessian(hess, isPoi)
    eig, ev = np.linalg.eigh(phess)
    # reorder to have larger ones first
    eig, ev = eig[::-1], ev[:, ::-1]
    print(f"Profile hessian eigenvalues: {eig}")

    above_threshold = eig >= args.threshold
    neig = above_threshold.sum()
    print(f"Values above threshold: {neig}")
    rotation = ev[:, above_threshold]
    expected_unc = 1 / np.sqrt(eig[above_threshold])
    ranges = 5 * expected_unc
    if args.scaleByEigenvalue:
        # we will multiply scalings to the left and right
        rotation *= expected_unc[None, :]
        ranges = 5 * np.ones(neig)
    print(rotation)
    print(ranges)

    scaling = read_scaling(args.scalingIn)
    output = []
    for item in scaling:
        take_to_pass = []
        take_to_rotate = []
        put_to_rotate = []
        for sidx, param in enumerate(item["parameters"]):
            paramname = re.sub(r"\[.*", "", param)
            if paramname in poinames:
                take_to_rotate.append(sidx)
                put_to_rotate.append(poinames.index(paramname))
            else:
                take_to_pass.append(sidx)
        print(f"Will rotate {take_to_rotate} in {item['channel']} {item['process']}")
        new_parameters = [item["parameters"][idx] for idx in take_to_pass] + [f"EV{i}[0,{-r},{r}]" for i, r in enumerate(ranges)]
        print(new_parameters)
        npar = len(item["parameters"])
        this_rotation = np.zeros((npar, len(new_parameters)))
        for put, take in enumerate(take_to_pass):
            this_rotation[take, put] = 1.0
        npass = len(take_to_pass)
        for iev in range(neig):
            for take, put in zip(take_to_rotate, put_to_rotate):
                this_rotation[take, npass + iev] = rotation[put, iev]
        this_scaling = _tril_to_square(item["scaling"], npar)
        assert np.allclose(_square_to_tril(this_scaling), item["scaling"])
        new_scaling = _square_to_tril(this_rotation.T @ this_scaling @ this_rotation)
        print(f"npar {len(new_parameters)} scaling shape {new_scaling.shape}")
        this_output = dict(item)
        this_output.update(parameters=new_parameters, scaling=new_scaling)
        output.append(this_output)

    with gzip.open(args.scalingOut, "wb") as fout:
        pickle.dump(output, fout)
