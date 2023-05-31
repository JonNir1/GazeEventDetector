import numpy as np
from warnings import warn as Warn
from typing import Tuple, List, Optional

import constants as cnst
from LWS.DataModels.LWSSubjectInfo import LWSSubjectInfo
from LWS.DataModels.LWSArrayStimulus import LWSArrayStimulus
from LWS.DataModels.LWSBehavioralData import LWSBehavioralData
from GazeEvents.BaseGazeEvent import BaseGazeEvent


class LWSTrial:
    """
    Represents a single trial in the LWS Demo experiment.
    """

    # TODO: encode as hdf5 file

    def __init__(self,
                 trial_num: int,
                 subject_info: LWSSubjectInfo,
                 stimulus: LWSArrayStimulus,
                 behavioral_data: LWSBehavioralData,
                 gaze_events: List[BaseGazeEvent] = None):
        self.__is_processed: bool = False
        self.__trial_num: int = trial_num
        self.__subject_info: LWSSubjectInfo = subject_info
        self.__stimulus: LWSArrayStimulus = stimulus
        self.__behavioral_data: LWSBehavioralData = behavioral_data
        self.__gaze_events: List[BaseGazeEvent] = sorted(self.__gaze_events,
                                                         key=lambda e: e.start_time) if gaze_events is not None else []

    @property
    def trial_num(self) -> int:
        return self.__trial_num

    @property
    def sampling_rate(self) -> float:
        return self.__behavioral_data.sampling_rate

    @property
    def is_processed(self) -> bool:
        return self.__is_processed

    @is_processed.setter
    def is_processed(self, is_processed: bool):
        if self.__is_processed and not is_processed:
            raise RuntimeError("Cannot set is_processed to False after it has been set to True.")
        self.__is_processed = is_processed

    def get_subject_info(self) -> LWSSubjectInfo:
        return self.__subject_info

    def get_stimulus(self) -> LWSArrayStimulus:
        return self.__stimulus

    def get_behavioral_data(self) -> LWSBehavioralData:
        return self.__behavioral_data

    def set_behavioral_data(self, behavioral_data: LWSBehavioralData):
        if self.is_processed:
            raise RuntimeError("Cannot set behavioral data after trial has been processed.")
        self.__behavioral_data = behavioral_data

    def get_gaze_events(self, event_type: Optional[str]) -> List[BaseGazeEvent]:
        if self.__gaze_events is None:
            return []
        if len(self.__gaze_events) == 0:
            return []
        if event_type is None:
            return self.__gaze_events

        event_type = event_type.lower()
        if event_type == cnst.ALL:
            return self.__gaze_events
        return list(filter(lambda e: e.event_type() == event_type, self.__gaze_events))

    def set_gaze_events(self, gaze_events: List[BaseGazeEvent]):
        if self.is_processed:
            raise RuntimeError("Cannot set gaze events after trial has been processed.")
        ge = self.get_gaze_events(event_type=cnst.ALL)
        if len(ge) > 0:
            Warn("Overwriting existing gaze events.")
        self.__gaze_events = sorted(gaze_events, key=lambda e: e.start_time)

    def get_raw_gaze_coordinates(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Returns the timestamp, x and y coordinates of the gaze data for the dominant eye.
        bd = self.get_behavioral_data()
        ts = bd.get(cnst.MICROSECONDS).values / 1000
        eye = self.get_subject_info().dominant_eye.lower()
        if eye == 'left':
            x = bd.get(cnst.LEFT_X).values
            y = bd.get(cnst.LEFT_Y).values
        elif eye == 'right':
            x = bd.get(cnst.RIGHT_X).values
            y = bd.get(cnst.RIGHT_Y).values
        else:
            raise ValueError(f'Invalid dominant eye: {eye}')
        return ts, x, y

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}_S{self.__subject_info.subject_id}_T{self.__trial_num}"

    def __str__(self) -> str:
        return self.__repr__()
