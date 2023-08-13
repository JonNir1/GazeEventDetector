import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
# from typing import Optional, Tuple, List, Union, Dict

import constants as cnst
import playground_helpers as ph
from Config import experiment_config as cnfg
import Visualization.visualization_utils as visutils

##########################################
### RUN PIPELINE / LOAD DATA  ############
##########################################

# subjects: "GalChen Demo" (001), "Rotem Demo" (002)
pipline_config = {'save': True, 'skip_analysis': True, 'verbose': True}

subject1, subject1_analysis, failed_trials1 = ph.full_pipline(name="GalChen Demo", **pipline_config)
del subject1_analysis, failed_trials1

# subject2, subject2_analysis, failed_trials2 = ph.full_pipline(name="Rotem Demo", **pipline_config)
# del subject2_analysis, failed_trials2

del pipline_config

# subject1 = ph.load_subject(subject_id=1, verbose=True)
# subject2 = ph.load_subject(subject_id=2, verbose=True)


##########################################
### PLAYGROUND  ##########################
##########################################

import LWS.analysis_scripts.looking_without_seeing as lws

all_trials = subject1.get_all_trials()
thresholds = np.arange(0.1 * cnfg.THRESHOLD_VISUAL_ANGLE,
                       1.2 * cnfg.THRESHOLD_VISUAL_ANGLE,
                       0.1 * cnfg.THRESHOLD_VISUAL_ANGLE)
lws_counts = np.zeros((subject1.num_trials, len(thresholds)))

for i, thrsh in enumerate(thresholds):
    lws_counts[:, i] = [lws.count_lws_fixations_per_trial(trial, proximity_threshold=thrsh) for trial in all_trials]

