from IPython.display import Image, display

class TrackProgress_MELA(object):
    def __init__(self):
        self.passed_simple_reweighting = False
        self.passed_enum = False
        self.passed_coupling = False
        self.passed_named_coupling = False
        self.created_input = False
        self.passed_ggH = False
        self.passed_EW = False
        self.WW = False
        self.affirm_yes = False
        self.passed_xsec = False
        
        self.image = Image(url="https://media.tenor.com/oEGwWZ9rYiYAAAAM/oksunglasses.gif")
        self.pass_overall = Image(url="https://palletfly-public.s3.amazonaws.com/product_images/16630-primary.jpg")
        self.try_again = Image(url="https://thumbs.dreamstime.com/b/try-again-dark-metal-icon-isolated-white-background-89083710.jpg")
    
    def final_check(self):
        if (
            self.passed_simple_reweighting and
            self.passed_enum and 
            self.passed_coupling and
            self.passed_named_coupling and
            self.created_input and
            self.passed_ggH and
            self.passed_EW and
            self.WW and
            self.affirm_yes and
            self.passed_xsec
        ):
            print("CONGRATS! YOU ARE A MELA MASTER")
            return self.pass_overall
        
        print("Looks like you missed an assert test! Try and finish all the tasks at hand!")
        return self.try_again
    
    def simple_reweight_pass(self):
        self.passed_simple_reweighting = True
        return self.image
    
    def enum_pass(self):
        self.passed_enum = True
        return self.image

    def coupling_pass(self):
        self.passed_coupling = True
        return self.image

    def named_coupling_pass(self):
        self.passed_named_coupling = True
        return self.image
    
    def ggH_reweight_pass(self):
        self.passed_ggH = True
        return self.image
    
    def WW_pass(self):
        self.WW = True
        return self.image
    
    def xsec_pass(self):
        self.passed_xsec = True
        return self.image
    
    def input_create_pass(self):
        self.created_input = True
        return self.image
    
    def EW_pass(self):
        self.passed_EW = True
        return self.image
    
    def affirm_pass(self):
        self.affirm_yes = True
        return self.image
        
    