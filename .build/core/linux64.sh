source ~/miniforge3/etc/profile.d/conda.sh
conda activate fiat_build
pyinstaller "linux64_build.spec" --distpath ../../bin/core --workpath ../../bin/core/intermediates