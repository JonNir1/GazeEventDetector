import os
import time
import numpy as np
import pandas as pd
import pickle as pkl
import cv2
import matplotlib.pyplot as plt
# from typing import Optional, Tuple, List, Union, Dict

import constants as cnst
import experiment_config as cnfg
from Utils.ScreenMonitor import ScreenMonitor
from LWS.DataModels.LWSTrial import LWSTrial
from LWS.DataModels.LWSTrialVisualizer import LWSTrialVisualizer

##########################################

start = time.time()

sm = ScreenMonitor.from_config()
trials = [LWSTrial.from_pickle(os.path.join(cnfg.OUTPUT_DIR, "S002", "trials", f"LWSTrial_S2_T{i+1}.pkl")) for i in range(1)]
visualizer = LWSTrialVisualizer(screen_resolution=sm.resolution, output_directory=cnfg.OUTPUT_DIR)

end = time.time()
print(f"Finished loading in: {(end - start):.2f} seconds")

start = time.time()

for tr in trials:
    if tr.trial_num > 1:
        break
    start_trial = time.time()
    # visualizer.create_gaze_figure(trial=tr, savefig=True)
    # visualizer.create_targets_figure(trial=tr, savefig=True)
    visualizer.create_video(trial=tr, output_directory=cnfg.OUTPUT_DIR)
    end_trial = time.time()
    print(f"\t{tr.__repr__()}:\t{(end_trial - start_trial):.2f} s")

end = time.time()
print(f"Finished visualization in: {(end - start):.2f} seconds")

# delete irrelevant variables:
del start
del end

##########################################

import LWS.PreProcessing as pp
# from LWS.DataModels.LWSFixationEvent import LWSFixationEvent

start = time.time()

trials = pp.process_subject(subject_dir=os.path.join(cnfg.RAW_DATA_DIR, 'Rotem Demo'),
                            stimuli_dir=cnfg.STIMULI_DIR,
                            screen_monitor=sm,
                            save_pickle=True,
                            stuff_with='fixation',
                            blink_detector_type='missing data',
                            saccade_detector_type='engbert',
                            drop_outlier_events=False)

# for i, tr in enumerate(trials):
#     fixations: List[LWSFixationEvent] = tr.get_gaze_events(cnst.FIXATION)
#     fixations_target_distances = np.array([f.visual_angle_to_target for f in fixations])
#     if any(fixations_target_distances <= 1.5):
#         break

end = time.time()
print(f"Finished preprocessing in: {(end - start):.2f} seconds")

# delete irrelevant variables:
del start
del end


