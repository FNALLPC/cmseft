# EFT Workshop 2025 Re-weighting Tutorial

This is the folder for the re-weighting tutorial using JHUGen-MELA.

## Setup


1. Logging In

We will be working on whatever server you want that **supports CMSSW** in Jupyter Notebooks.
To that end, we will also initiate them in the server. Login using the following command:

```bash
ssh -L localhost:8888:localhost:8888 <username>@<servername>
```

2. Setting Things Up

Run the following command:

```bash
./setup.sh
eval $(./CMSSW_14_0_0/src/JHUGenerator.v7.5.7/JHUGenMELA/MELA)
```

From there, navigate to this folder, and run the following:

```bash
jupyter notebook --no-browser --port 8888
```

