import importlib.resources
import pickle
import re
import xml.etree.ElementTree as ET
from math import prod
from pathlib import Path
from typing import Any, Dict, List, Tuple
import os
import numpy as np
import xmltodict
from PIL import Image
from pint import Quantity, UnitRegistry
from scipy.sparse import csr_matrix
from scipy.stats import variation
from skimage.filters import threshold_mean
from skimage.morphology import area_closing, closing, disk
from skimage.segmentation import morphological_geodesic_active_contour as MorphGAC
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from .input_channels_3D import IMC_3D_input_channels
from .segmentation_2D_slices import segmentation
from .match_2D_stacks import match_stacks
from .match_3D_cells import match_3D_cells
# from .single_method_eval_3D import eval_3D

def universal_2Dto3D(input_dir, output_dir):
	# get input channels
	nucleus, cytoplasm, membrane = IMC_3D_input_channels(input_dir)
	
	# segmentation for each slice on XY, YZ, XZ axes
	segmentation(nucleus, cytoplasm, membrane, os.path.dirname(input_dir))
	
	# 2D-3D reconstruction
	mask_matched_XY, mask_matched_XZ, mask_matched_YZ = match_stacks(os.path.dirname(input_dir))
	mask_3D = match_3D_cells(mask_matched_XY, mask_matched_XZ, mask_matched_YZ, os.path.dirname(input_dir))
	
	return mask_3D
