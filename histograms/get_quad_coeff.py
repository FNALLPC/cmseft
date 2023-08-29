import os
import json
import argparse
from coffea.nanoevents import NanoEventsFactory

# silence warnings due to using NanoGEN instead of full NanoAOD
from coffea.nanoevents import NanoAODSchema
NanoAODSchema.warn_missing_crossrefs = False

from topcoffea.scripts.make_html import make_html
from topcoffea.modules import utils
import topcoffea.modules.quad_fit_tools as qft

LIM_DICT = {
    "cHtbIm" : [-2,2],
    "cHtbRe" : [-2,2],
    "ctGIm"  : [-2,2], 
    "cHt"    : [-2,2], 
    "ctGRe"  : [-2,2], 
    "ctWRe"  : [-2,2], 
    "ctWIm"  : [-2,2], 
    "ctBIm"  : [-2,2], 
    "ctBRe"  : [-2,2],
}

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("-o", "--output-path",default=".")
    parser.add_argument("-n", "--outdir-name",default="quad_fit_info")
    args = parser.parse_args()

    # Get the info from the input file
    events = NanoEventsFactory.from_root(args.input_file).events()
    wc_names_lst = utils.get_list_of_wc_names(args.input_file)

    # Get the array of fit coeffecients and dump into a dict (so that we can e.g. plot 1d quads)
    wc_fit_arr = qft.get_summed_quad_fit_arr(events)
    wc_fit_dict = qft.get_quad_fit_dict(wc_names_lst,wc_fit_arr)
    wc_fit_dict = qft.scale_to_sm(wc_fit_dict)

    # Make an output directory
    save_dir_path = args.output_path
    if not os.path.exists(os.path.join(args.output_path,args.outdir_name)):
        os.mkdir(args.outdir_name)
        save_dir_path = os.path.join(args.output_path,args.outdir_name)
    else:
        raise Exception("Output path already exists.")

    # Dump all coeffs to json
    json_name = "quad_fit_coeff.json"
    out_loc = os.path.join(args.output_path,args.outdir_name)
    print("\nDumping quad fit coeff to json..")
    with open(json_name,"w") as out_file:
        json.dump(wc_fit_dict,out_file,indent=4)

    # Make 1d quad plots for all the WCs
    print("\nMaking 1d quad plots...")
    yaxis_str = "$\sigma/\sigma_{SM}$"
    for wc_name in wc_names_lst:
        fit_coeffs_1d = qft.get_1d_fit(wc_fit_dict,wc_name)
        qft.make_1d_quad_plot(
            {wc_name: fit_coeffs_1d},
            wc_name,
            yaxis_str,
            title=wc_name,
            xaxis_range = LIM_DICT[wc_name],
            save_dir=save_dir_path,
        )


if __name__ == "__main__":
    main()
