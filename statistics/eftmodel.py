import json

from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModelBase
import ROOT


class EFTModel(PhysicsModelBase):
    def __init__(self, coeff_file):
        with open(coeff_file) as fin:
            self.quad_fit = json.load(fin)
        self.pois = set()
        for key in self.quad_fit:
            wc1, wc2 = key.split("*")
            self.pois.add(wc1)
            self.pois.add(wc2)
        self.pois.remove("sm")

    def doParametersOfInterest(self):
        for poi in sorted(self.pois):
            # here we may want custom ranges per POI
            self.modelBuilder.doVar(poi + "[0,-3,3]")
        self.modelBuilder.doSet("POI", ",".join(sorted(self.pois)))

    def getYieldScale(self, channel, process):
        if process == "ttbar" and channel == "SR":
            terms = []
            for term, scale in self.quad_fit.items():
                term = term.replace("sm", "1.0")
                terms.append(f"{scale}*{term}")
            formula = "+".join(terms)
            fvars = ",".join(self.pois)
            self.modelBuilder.factory_(f'expr::scaling_ttbar_SR("{formula}", {fvars})')
            return "scaling_ttbar_SR"


eftModel = EFTModel("quad_fit_coeff.json")
