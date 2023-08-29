#!/bin/bash
set -e

# Set up the environment
unset PYTHONPATH # To avoid conflicts 

if [ -x "$(command -v mamba)" ]; then
  if [ -x "$(command -v conda)" ]; then
    echo "Conda not found, please install mambaforge by following the instructions"
    echo " at https://github.com/conda-forge/miniforge#install"
  else
    conda install -y mamba
  fi
fi

if ! mamba env list|grep -q coffea-env; then
  mamba create --name coffea-env -c conda-forge --strict-channel-priority -y python=3.9 numpy=1.23.5 coffea
fi
mamba activate coffea-env

if [ ! -d topcoffea ]; then
  # Install the topcoffea dependency
  git clone -b new_histEFT https://github.com/btovar/topcoffea.git
  pushd topcoffea
  pip install -e .
  popd
fi

# Get the example data file
wget -nc http://www.crc.nd.edu/~kmohrman/files/root_files/for_tutorial/from_daniel/nanogen_small.root
