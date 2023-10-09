# Setting up..
echo "Locating conda.."
conda_executable=$(which conda)
conda_base_dir=$(dirname $(dirname $conda_executable))
source $conda_base_dir/etc/profile.d/conda.sh

# Do the thing!
echo "Build stuff.."
conda activate fiat_build
export PROJ_LIB=/usr/share/proj
pyinstaller "linux64.spec" --distpath ../bin --workpath ../bin/intermediates
