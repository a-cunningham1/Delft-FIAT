source ~/miniforge3/etc/profile.d/conda.sh
conda activate fiat_build
export PROJ_LIB=/usr/share/proj
pyinstaller "linux64.spec" --distpath ../bin --workpath ../bin/intermediates