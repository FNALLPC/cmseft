#!/bin/bash

# Set up the environment
unset PYTHONPATH # To avoid conflicts 
conda create --name coffea-env -c conda-forge --strict-channel-priority -y python=3.9 numpy=1.23.5 coffea # Create conda env, took like 50m on lxplus... 
conda activate coffea-env

# Install the topcoffea dependency
git clone -b new_histEFT https://github.com/btovar/topcoffea/tree/new_histEFT
cd topcoffea
pip install -e .
cd ..

# Get the example data file
wget -nc http://www.crc.nd.edu/~kmohrman/files/root_files/for_tutorial/from_daniel/nanogen_small.root
