import numpy as np
import pandas as pd
from abc import ABC, abstractmethod


class BaseGazeEvent(ABC):

    __MINIMUM_TIMESTAMPS_FOR_EVENT = 2

    def __init__(self, timestamps: np.ndarray, sampling_rate: float):
        if len(timestamps) < self.__MINIMUM_TIMESTAMPS_FOR_EVENT:
            raise ValueError("event must be at least {} samples long".format(self.__MINIMUM_TIMESTAMPS_FOR_EVENT))
        if np.isnan(timestamps).any() or np.isinf(timestamps).any():
            raise ValueError("array timestamps must not contain NaN values")
        if (timestamps < 0).any():
            raise ValueError("array timestamps must not contain negative values")
        if np.isnan(sampling_rate) or np.isinf(sampling_rate):
            raise ValueError("sampling_rate must not be NaN or infinite")
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be greater than 0")
        self.__timestamps = timestamps
        self.__sampling_rate = sampling_rate

    def to_series(self) -> pd.Series:
        """
        creates a pandas Series with summary of event information.
        :return: a pd.Series with the following index:
            - start_time: event's start time in milliseconds
            - end_time: event's end time in milliseconds
            - duration: event's duration in milliseconds
            - sampling_rate: the sampling rate used to record the event
            - is_outlier: boolean indicating whether the event is an outlier or not
        """
        return pd.Series(data=[self.event_type(), self.start_time, self.end_time,
                               self.duration, self.__sampling_rate, self.is_outlier],
                         index=["event_type", "start_time", "end_time",
                                "duration", "sampling_rate", "is_outlier"])

    @property
    def start_time(self) -> float:
        # Event's start time in milliseconds
        return self.__timestamps[0]

    @property
    def end_time(self) -> float:
        # Event's end time in milliseconds
        return self.__timestamps[-1]

    @property
    def duration(self) -> float:
        # Event's duration in milliseconds
        return self.end_time - self.start_time

    @property
    @abstractmethod
    def is_outlier(self) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def event_type(cls) -> str:
        raise NotImplementedError

    def __repr__(self):
        return f"{self.event_type().capitalize()} ({self.duration:.1f} ms)"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        if self.__sampling_rate != other.__sampling_rate:
            return False
        if self.__timestamps.shape != other.__timestamps.shape:
            return False
        if not np.allclose(self.__timestamps, other.__timestamps):
            return False
        return True
