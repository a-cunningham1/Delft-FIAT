#!/usr/bin/bash 
# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

# Extract the GDAL version number
version=gdalinfo --version | cut -d' ' -f2
# Remove the annoying comma
version=${version%,}

# Make the yaml and create the environment
python $SCRIPTPATH/../make_env.py build
mamba env create -f environment.yml

# Set the appropriate env variables for GDAL
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal

# Install GDAL and FIAT
conda activate fiat_build
pip install --no-cache-dir gdal==$version
pip install -e .
conda deactivate

# Clear the conda and pip cache
conda_executable=$(which conda)
conda_base_dir=$(dirname $(dirname $conda_executable))
rm -rf $conda_base_dir/pkgs/*
pip cache purge