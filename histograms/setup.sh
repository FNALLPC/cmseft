#!/bin/bash

# Set up the environment
unset PYTHONPATH # To avoid conflicts 

if ! which mamba 2>/dev/null; then
  if ! which conda 2>/dev/null; then
    echo "Conda not found, please install mambaforge by following the instructions"
    echo " at https://github.com/conda-forge/miniforge#install"
  else
    conda activate base
    conda install -c conda-forge -y mamba
  fi
fi

conda activate base
if ! mamba env list|grep -q coffea-env; then
  mamba create --name coffea-env -c conda-forge --strict-channel-priority -y python=3.9 numpy=1.23.5 coffea
fi
conda activate coffea-env

if [ ! -d topcoffea ]; then
  # Install the topcoffea dependency
  git clone -b new_histEFT https://github.com/btovar/topcoffea.git
  pushd topcoffea
  pip install -e .
  popd
fi

# Get the example data file
wget -nc http://www.crc.nd.edu/~kmohrman/files/root_files/for_tutorial/from_daniel/nanogen_small.root
