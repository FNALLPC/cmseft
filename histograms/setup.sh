#!/bin/bash

# Set up the environment
unset PYTHONPATH # To avoid conflicts 

if [ "$(which conda 2>/dev/null)" == "" ]; then
  echo "Conda not found, please install mambaforge by following the instructions"
  echo " at https://github.com/conda-forge/miniforge#install"
  exit
elif [ "$(which conda 2>/dev/null)" == "/usr/bin/conda" ]; then
  echo "Conda found, but not where you want it! Please install mambaforge by following the instructions"
  echo " at https://github.com/conda-forge/miniforge#install"
  exit
fi

if ! conda env list|grep -q coffea-env; then
  # mamba create --name coffea-env -c conda-forge --strict-channel-priority -y python=3.9 numpy=1.23.5 coffea
  conda env create -f environment.yml
fi
conda activate coffea-env

if [ ! -d dir_for_topcoffea ]; then
  # Install the topcoffea dependency
  mkdir dir_for_topcoffea
  cd dir_for_topcoffea
  git clone https://github.com/TopEFT/topcoffea.git
  cd topcoffea
  pip install -e .
  cd ../..
fi

# Get the example data file
wget -nc http://www.crc.nd.edu/~kmohrman/files/root_files/for_tutorial/from_daniel/nanogen_small.root
