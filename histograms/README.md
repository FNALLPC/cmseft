# histograms

## Setup instructions

Assuming the `cmseft2023` repo has already been cloned, just run the setup script:
```
cd cmseft2023/histograms
source setup.sh
```

## Running the processor
Run the processor over the example root file.
```
python run_processor.py example_sample.json
```
## Other things to try

You can try exploring the quadratic parameterization with `get_quad_coeff.py`. This script explores some of the contents of the nanogen root file. The script will open the file, extract the WC quadratic fit coefficients for each event and sum them (so we are just looking at inclusive parametrization). It will then the quadratic fit coefficients into a json that you can take a look at. It will also make some simple 1d plots of the 1d slices of the n-dimensional quadratic parameterization. 
```
python get_quad_coeff.py nanogen_small.root
```

To explore the output histogram (from the running the processor step), you can take a look at the resulting histograms and try to reweight to a non-SM point to see how it compares to the shape and normalization at the SM. E.g.:
```
python plotter.py histos.pkl.gz
```
