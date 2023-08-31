import ROOT as rt
import numpy as np
import glob, sys, os
import pandas as pd
import argparse

if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--poi", help="POI for 2D likelihood scan separated by comma")

    args = argParser.parse_args()
    poi = str(args.poi)
    
    if len(poi) < 1:
        sys.exit("No POI provided")

    poi = poi.split(',')
    if len(poi) != 2:
        sys.exit("Wrong number of POI provided")

    print(poi)

    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetPadRightMargin(0.25)

    c = rt.TCanvas("c", "c", 500, 400)

    limit = rt.TChain("limit")

    # Check both orders for POI in file name
    filename1 = "higgsCombineScan2D."+poi[0]+"."+poi[1]+".MultiDimFit.mH120.root"
    filename2 = "higgsCombineScan2D."+poi[1]+"."+poi[0]+".MultiDimFit.mH120.root"

    if os.path.isfile(filename1):
        for ifile in glob.glob(filename1):
            limit.Add(ifile)
    elif os.path.isfile(filename2):
        for ifile in glob.glob(filename2):
            limit.Add(ifile)
    else:
        sys.exit("No root file found. Did you run the likelihood scan with combine?")

    deltaNLL = []
    poi0 = []
    poi1 = []

    for x in limit:
        deltaNLL += [getattr(x, 'deltaNLL')]
        poi0 += [ getattr(x,poi[0])]
        poi1 += [ getattr(x,poi[1])]

    poi0_min = min(poi0)
    poi0_max = max(poi0)
    poi0_nbins = len(np.unique(poi0))-1
    poi0_step = 1.0*(poi0_max - poi0_min)/poi0_nbins

    poi1_min = min(poi1)
    poi1_max = max(poi1)
    poi1_nbins = len(np.unique(poi1))-1
    poi1_step = 1.0*(poi1_max - poi1_min)/poi1_nbins

    h = rt.TH2D("h","h",
                poi0_nbins, poi0_min - 0.5*poi0_step, poi0_max + 0.5*poi0_step,
                poi1_nbins, poi1_min - 0.5*poi1_step, poi1_max + 0.5*poi1_step)

    for i,val in enumerate(deltaNLL):
        print(i)
        print(poi0[i],poi1[i])
        h.Fill(poi0[i],poi1[i],val)

    h.GetXaxis().SetTitle(poi[0]);
    h.GetYaxis().SetTitle(poi[1]);
    h.GetZaxis().SetTitle("2#DeltaNLL");
    h.Draw('COLZ')

#    c.Print("Scan2D_"+poi+".pdf")
    c.Print("Scan2D_"+poi[0]+"_"+poi[1]+".png")
