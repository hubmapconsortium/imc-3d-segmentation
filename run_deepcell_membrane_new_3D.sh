#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate deepcell_new
python deepcell_wrapper_membrane_new_3D.py $1 XY
python deepcell_wrapper_membrane_new_3D.py $1 YZ
python deepcell_wrapper_membrane_new_3D.py $1 XZ
conda deactivate
