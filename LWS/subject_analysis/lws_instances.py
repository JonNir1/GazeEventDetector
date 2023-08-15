import numpy as np
import pandas as pd
from typing import List, Union
from itertools import pairwise

import constants as cnst
import Config.experiment_config as cnfg
import Utils.array_utils as arr_utils
from LWS.DataModels.LWSTrial import LWSTrial
from LWS.DataModels.LWSFixationEvent import LWSFixationEvent
from GazeEvents.GazeEventEnums import GazeEventTypeEnum
from GazeEvents.SaccadeEvent import SaccadeEvent


def calculate_lws_rate(trial: LWSTrial,
                       proximity_threshold: float = cnfg.THRESHOLD_VISUAL_ANGLE,
                       proximal_fixations_only: bool = False) -> float:
    """
    Calculates the LWS rate for the given trial, which is the fraction of fixations that are LWS instances out of
    (a) all fixations in the trial; or (b) only the proximal fixations in the trial, depending on the value of the flag
    `proximal_fixations_only`.
    """
    is_lws_instance = identify_lws_instances(trial, proximity_threshold=proximity_threshold)
    num_lws_instances = np.nansum(is_lws_instance)
    fixations = trial.get_gaze_events(event_type=GazeEventTypeEnum.FIXATION)
    if proximal_fixations_only:
        fixations = list(filter(lambda f: f.visual_angle_to_closest_target <= proximity_threshold, fixations))
    num_fixations = len(fixations)
    if num_fixations > 0:
        return num_lws_instances / num_fixations
    if num_lws_instances == 0:
        return 0
    raise ZeroDivisionError(f"num_lws_instances = {num_lws_instances},\tnum_fixations = {num_fixations}")


def identify_lws_instances(trial: LWSTrial,
                           proximity_threshold: float = cnfg.THRESHOLD_VISUAL_ANGLE) -> List[Union[bool, float]]:
    """
    Identifies the LWS instances in the given trial, and returns a list of the same length as the trial's gaze events,
    where each element is either:
        - True: if the corresponding fixation event is a LWS instance
        - False: if the corresponding fixation event is not a LWS instance
        - np.nan: if the corresponding gaze event is not a fixation

    See identification criteria in the docstring of `_check_lws_instance_standalone_criteria` and
    `_check_lws_instance_pairwise_criteria`.

    Note: this function assumes that the trial's gaze events are sorted by their start time.
    """
    target_info = _target_identification_data(trial, proximity_threshold=proximity_threshold)
    events = trial.get_gaze_events()
    fixation_idxs = np.where([e.event_type() == GazeEventTypeEnum.FIXATION for e in events])[0]
    is_lws_instance = np.full_like(events, np.nan)

    # start with the last fixation
    last_fixation_idx = fixation_idxs[-1]
    is_lws_instance[last_fixation_idx] = _check_lws_instance_standalone_criteria(events[last_fixation_idx], target_info,
                                                                                 proximity_threshold)

    # work our way backwards in pairs of fixations
    fixation_pair_idxs = list(pairwise(fixation_idxs))
    for curr_fixation_idx, next_fixation_idx in fixation_pair_idxs[::-1]:
        curr_fixation = events[curr_fixation_idx]
        next_fixation = events[next_fixation_idx]
        if not _check_lws_instance_standalone_criteria(curr_fixation, target_info, proximity_threshold):
            # current fixation does not meet the standalone criteria for a LWS instance
            is_lws_instance[curr_fixation_idx] = False
            continue
        if not _check_lws_instance_pairwise_criteria(curr_fixation, next_fixation,
                                                     is_next_fixation_lws_instance=is_lws_instance[next_fixation_idx]):
            # current fixation does not meet the pairwise criteria for a LWS instance
            is_lws_instance[curr_fixation_idx] = False
            continue
        # current fixation meets both the standalone and pairwise criteria for a LWS instance
        is_lws_instance[curr_fixation_idx] = True
    return list(is_lws_instance)


def _target_identification_data(trial: LWSTrial,
                                proximity_threshold: float = cnfg.THRESHOLD_VISUAL_ANGLE,
                                identification_seq: np.ndarray = cnfg.TARGET_IDENTIFICATION_SEQUENCE) -> pd.DataFrame:
    """
    For each of the trial's targets, extracts the following information:
        - icon_path: full path to the icon file
        - icon_category: category of the icon (face, animal, etc.)
        - center_x: x coordinate of the icon center
        - center_y: y coordinate of the icon center
        - distance_identified: distance (in visual angle) between the target and the gaze when the target was
            identified by the subject
        - time_identified: time (in milliseconds) when the target was identified by the subject
        - time_confirmed: time (in milliseconds) when the target was confirmed by the subject

    Returns a dataframe with shape (num_targets, 7), where each row corresponds to a target.
    """
    if proximity_threshold is not None and (proximity_threshold <= 0 or np.isinf(proximity_threshold)):
        raise ValueError(f"Invalid `proximity_threshold`: {proximity_threshold}")
    if np.isnan(proximity_threshold):
        proximity_threshold = None

    # extract relevant columns from the behavioral data
    behavioral_data = trial.get_behavioral_data()
    columns = ([cnst.MICROSECONDS, cnst.TRIGGER, "closest_target"] +
               [col for col in behavioral_data.columns if col.startswith(f"{cnst.DISTANCE}_{cnst.TARGET}")])
    behavioral_df = pd.DataFrame(behavioral_data.get(columns), columns=columns)

    res = pd.DataFrame(np.full((trial.num_targets, 3), np.nan),
                       columns=["distance_identified", "time_identified", "time_confirmed"])
    for i in range(trial.num_targets):
        proximal_behavioral_df = behavioral_df[behavioral_df["closest_target"] == i]

        # check if target was ever identified by the subject
        identification_idxs = arr_utils.find_sequences_in_sparse_array(proximal_behavioral_df[cnst.TRIGGER].values,
                                                                       sequence=identification_seq)
        if len(identification_idxs) == 0:
            # this target was never identified
            continue

        # check if any of the target's identification attempts were from below the threshold distance
        identification_distances = np.array(
            [proximal_behavioral_df.iloc[first_idx][f"{cnst.DISTANCE}_{cnst.TARGET}{i}"]
             for first_idx, last_idx in identification_idxs])
        proximal_identifications = np.where(identification_distances < proximity_threshold)[0]
        if len(proximal_identifications) == 0:
            # no proximal identification attempts
            continue

        # find the start & end idxs of the first identification attempt that was from below the threshold distance
        first_proximal_identification = min(proximal_identifications)
        first_proximal_identification_idxs = identification_idxs[first_proximal_identification]
        first_idx, last_idx = first_proximal_identification_idxs
        res.loc[i, "distance_identified"] = proximal_behavioral_df.iloc[first_idx][
            f"{cnst.DISTANCE}_{cnst.TARGET}{i}"]
        res.loc[i, "time_identified"] = proximal_behavioral_df.iloc[first_idx][
                                            cnst.MICROSECONDS] / cnst.MICROSECONDS_PER_MILLISECOND
        res.loc[i, "time_confirmed"] = proximal_behavioral_df.iloc[last_idx][
                                           cnst.MICROSECONDS] / cnst.MICROSECONDS_PER_MILLISECOND
    return pd.concat([trial.get_targets(), res], axis=1)


def _check_lws_instance_standalone_criteria(fixation: LWSFixationEvent,
                                            target_identification_data: pd.DataFrame,
                                            proximity_threshold: float = cnfg.THRESHOLD_VISUAL_ANGLE) -> bool:
    """
    Checks if the given fixation meets the standalone criteria required for a LWS instance: fixation needs to be close
    to a target that was not identified up until the end of the fixation.
        - If the fixation is not close to any target, then it does not meet the criteria.
        - If the fixation is close to a never-identified target, then it meets the criteria.
        - If the fixation is close to a target that was identified *after* the fixation ended, then it meets the criteria.
        - Otherwise it does not meet the criteria.
    """
    if fixation.end_time == fixation.trial.end_time:
        # the trial ended during this fixation, so we cannot say that the subject was unaware of the target at the end
        # of the fixation --> return False
        return False
    if fixation.visual_angle_to_closest_target > proximity_threshold:
        # fixation is not close to any target, so it cannot be a LWS fixation --> return False
        return False
    closest_target_id = fixation.closest_target_id
    time_identified = target_identification_data.loc[closest_target_id, "time_identified"]
    if np.isnan(time_identified):
        # fixation is close to a never-identified target, so it may be a LWS fixation --> return True
        return True
    # if the fixation ended before the target was identified, then it could be a LWS fixation
    return fixation.end_time < time_identified


def _check_lws_instance_pairwise_criteria(curr_fixation: LWSFixationEvent,
                                          next_fixation: LWSFixationEvent,
                                          is_next_fixation_lws_instance: bool) -> bool:
    """
    Checks if the given fixation meets the pairwise criteria required for a LWS instance:
        - If the next fixation is in the target-helper region of the stimulus, then the current fixation doesn't meet
            the criteria.
        - If the next fixation is on a different target, then the current fixation meets the criteria.
        - If the next fixation is on the same target, but it started too long after the current fixation ended, then
            the current fixation meets the criteria.
        - Otherwise the current fixation only meets the criteria if the next fixation is a LWS instance.
    """
    if next_fixation.is_in_rectangle(cnfg.STIMULUS_BOTTOM_STRIP_TOP_LEFT, cnfg.STIMULUS_BOTTOM_STRIP_BOTTOM_RIGHT):
        # next fixation is in the target-helper region of the stimulus, meaning that the subject (rightfully) suspects
        # that the current fixation is on a target --> the current fixation cannot be a LWS instance
        return False
    if next_fixation.closest_target_id != curr_fixation.closest_target_id:
        # next fixation is on a different target --> the current fixation could be a LWS instance
        return True
    if next_fixation.start_time - curr_fixation.end_time > SaccadeEvent.MAX_DURATION:
        # both fixations are on the same target, but the next fixation started too long after the current fixation
        # ended --> the current fixation could be a LWS instance
        return True

    # reached here if the subject uses both fixations to examine the same target, and they are close enough in time
    # for us to extrapolate from the next fixation onto the current one. so the current fixation is a LWS instance iff
    # the next fixation is also a LWS instance.
    return is_next_fixation_lws_instance