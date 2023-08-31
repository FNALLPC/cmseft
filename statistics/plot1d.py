import ROOT as rt
#from array import array
#from scipy.interpolate import Rbf
import numpy as np
import glob
import pandas as pd
import argparse

if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--poi", help="POI for 1D likelihood scan")

    args = argParser.parse_args()
    poi = args.poi

    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetPadRightMargin(0.15)

    c = rt.TCanvas("c", "c", 500, 400)

    limit = rt.TChain("limit")
    for ifile in glob.glob("higgsCombineScan1D."+poi+".MultiDimFit.mH120.root"):
        limit.Add(ifile)

    deltaNLL = []
    mu = []

    for x in limit:
        deltaNLL += [getattr(x, 'deltaNLL')]
        mu +=[ getattr(x,poi)]

    df = pd.DataFrame()
    df['mu'] = mu
    df['deltaNLL'] = deltaNLL
    df.drop_duplicates(inplace=True)
    df.sort_values('mu',inplace=True)

    g = rt.TGraph(len(df))
    for i in range(len(df)):
        g.SetPoint(i,df['mu'].iloc[i],2*df['deltaNLL'].iloc[i])
        g.SetMarkerStyle(34)
        g.SetMarkerSize(1.5)
    g.SetLineColor(1)
    g.SetLineWidth(3)

    g.GetXaxis().SetTitle(poi);
    g.GetYaxis().SetTitle("2#DeltaNLL");
    g.Draw('ac')

#    c.Print("Scan1D_"+poi+".pdf")
    c.Print("Scan1D_"+poi+".png")
