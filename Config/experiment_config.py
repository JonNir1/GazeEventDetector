"""
This file contains the configuration for each specific experiment.
"""
import os
import numpy as np

import constants as cnst
from Config.ScreenMonitor import ScreenMonitor

# DIRECTORIES
BASE_DIR = r"S:\Lab-Shared\Experiments\LWS Free Viewing Demo"
STIMULI_DIR = os.path.join(BASE_DIR, "Stimuli", "generated_stim1")
RAW_DATA_DIR = os.path.join(BASE_DIR, "RawData")
OUTPUT_DIR = os.path.join(BASE_DIR, "Results")

# GLOBAL VARIABLES
ADDITIONAL_COLUMNS = ["ConditionName", "BlockNum", "TrialNum", "ImageNum"]  # additional columns to be added to the gaze data
SCREEN_MONITOR: ScreenMonitor = ScreenMonitor.from_default()  # global variable: screen monitor object
VIEWER_DISTANCE = 65  # global variable: distance between subject and screen center (cm)


# GAZE DATA & GAZE EVENTS CONFIGURATION
EVENT_TYPES = [cnst.BLINK, cnst.SACCADE, cnst.FIXATION]

DEFAULT_MINIMUM_SAMPLES_PER_EVENT = 2  # minimum number of samples in an event (saccade, fixation, etc.)
DEFAULT_INTER_EVENT_TIME = 5  # minimal time between two (same) events in milliseconds (two saccades, two fixations, etc.)
DEFAULT_MISSING_VALUE = np.nan  # default value indicating missing data in the gaze data (x, y)

DEFAULT_BLINK_MINIMUM_DURATION = 50  # minimum duration of a blink in milliseconds

DEFAULT_SACCADE_MINIMUM_DURATION = 5  # minimum duration of a saccade in milliseconds

DEFAULT_FIXATION_MINIMUM_DURATION = 55  # minimum duration of a fixation in milliseconds
DEFAULT_FIXATION_MAX_VELOCITY = 20  # degrees per second

# LWS TRIGGERS CONFIGURATION
START_RECORDING_TRIGGER = 254  # trigger indicating the start of a trial
END_RECORDING_TRIGGER = 255  # trigger indicating the end of a trial
STIMULUS_ON_TRIGGER = 15  # trigger indicating the start of a stimulus presentation
STIMULUS_OFF_TRIGGER = 16  # trigger indicating the end of a stimulus presentation

MARK_TARGET_SUCCESSFUL_TRIGGER = 211  # trigger indicating the subject attempted to mark a target successfully
MARK_TARGET_UNSUCCESSFUL_TRIGGER = 212  # trigger indicating the subject attempted to mark target unsuccessfully
CONFIRM_TARGET_SUCCESSFUL_TRIGGER = 221  # trigger indicating the subject attempted to confirm a target successfully
CONFIRM_TARGET_UNSUCCESSFUL_TRIGGER = 222  # trigger indicating the subject attempted to confirm a target unsuccessfully
REJECT_TARGET_SUCCESSFUL_TRIGGER = 231  # trigger indicating the subject attempted to reject a target successfully
REJECT_TARGET_UNSUCCESSFUL_TRIGGER = 232  # trigger indicating the subject attempted to reject a target unsuccessfully

# LWS ANALYSIS CONFIGURATION
THRESHOLD_VISUAL_ANGLE = 1.5  # threshold for the visual angle between a target and a gaze datapoint, in degrees