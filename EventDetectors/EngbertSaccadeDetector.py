import numpy as np
from typing import List, Tuple

from Utils import velocity_utils as vu
from EventDetectors.BaseSaccadeDetector import BaseSaccadeDetector, DEFAULT_SACCADE_MINIMUM_DURATION

DEFAULT_DERIVATION_WINDOW_SIZE = 3
DEFAULT_LAMBDA_NOISE_THRESHOLD = 5


class EngbertSaccadeDetector(BaseSaccadeDetector):
    """
    Saccade detector based on the algorithm described by Engbert, Kliegl, and Mergenthaler (2003, 2006).
    See implementations in the following repositories:
        - https://github.com/Yuvishap/Gaze-Project/blob/67acb26fc90e5148a05b47ca7711306c94b79ed7/Gaze/src/pre_processing/business/EngbertFixationsLogic.py
        - https://github.com/odedwer/EyelinkProcessor/blob/66f56463ba8d2ad75f7935e3d020b051fb2aa4a4/SaccadeDetectors.py
        - https://github.com/esdalmaijer/PyGazeAnalyser/blob/master/pygazeanalyser/detectors.py#L175

    Defines these properties:
    - sampling_rate: sampling rate of the data in Hz
    - min_duration: minimum duration of a blink in milliseconds                     (default: 5)
    - inter_event_time: minimal time between two (same) events in ms                (default: 5)
    - derivation_window_size: size of the window used to calculate the derivative   (default: 3)
    - lambda_noise_threshold: threshold for the lambda noise value                  (default: 5)
    """

    def __init__(self,
                 sr: float,
                 min_duration: float = DEFAULT_SACCADE_MINIMUM_DURATION,
                 iet: float = BaseSaccadeDetector.DEFAULT_INTER_EVENT_TIME,
                 derivation_window_size: int = DEFAULT_DERIVATION_WINDOW_SIZE,
                 lambda_noise_threshold: int = DEFAULT_LAMBDA_NOISE_THRESHOLD):
        super().__init__(sr=sr, min_duration=min_duration, iet=iet)
        self.__derivation_window_size = derivation_window_size
        self.__lambda_noise_threshold = lambda_noise_threshold

    def detect(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        is_saccade_candidate = self._find_candidates(x, y)
        saccades_start_end_idxs = self._find_start_end_indices(is_saccade_candidate)

        # convert to boolean array
        saccade_idxs = np.concatenate([np.arange(start, end + 1) for start, end in saccades_start_end_idxs])
        is_saccade = np.zeros(len(x), dtype=bool)
        is_saccade[saccade_idxs] = True
        return is_saccade

    def _find_candidates(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Detects saccade candidates of a single eye, in the given gaze data.
        A saccade candidate is a sample that has a velocity greater than the noise threshold, calculated as the multiple
            of the velocity's median-standard-deviation with the constant self.__lambda_noise_threshold.
        :param x: gaze positions on the x-axis
        :param y: gaze positions on the y-axis

        :return: boolean array of the same length as the given data, indicating whether a sample is a saccade candidate

        :raises ValueError: if the given data is not of the same length
        :raises ValueError: if the given data is not of length at least 2 * self.derivation_window_size
        """
        if len(x) != len(y):
            raise ValueError("x and y must be of the same length")
        if len(x) < 2 * self.__derivation_window_size:
            raise ValueError(
                f"x and y must be of length at least 2 * derivation_window_size (={2 * self.__derivation_window_size})")

        vel_x = vu.numerical_derivative(x, n=self.__derivation_window_size)
        sd_x = vu.median_standard_deviation(vel_x)
        vel_y = vu.numerical_derivative(y, n=self.__derivation_window_size)
        sd_y = vu.median_standard_deviation(vel_y)

        ellipse_thresholds = np.power(vel_x / (sd_x * self.__lambda_noise_threshold), 2) + np.power(
            vel_y / (sd_y * self.__lambda_noise_threshold), 2)
        is_saccade_candidate = ellipse_thresholds > 1
        return is_saccade_candidate.values

    def _find_start_end_indices(self, is_saccade_candidate: np.ndarray) -> List[Tuple[int, int]]:
        """
        Excludes saccade candidates that are shorter than the minimum duration of a saccade.
        :param is_saccade_candidate: boolean array indicating whether a sample is a saccade candidate
        :return: list of tuples, each tuple containing the start and end indices of a saccade
        """
        # split saccade candidates to separate saccades
        saccade_candidate_idxs = np.nonzero(is_saccade_candidate)[0]
        splitting_idxs = np.where(np.diff(saccade_candidate_idxs) > self._min_samples_between_events)[
                             0] + 1  # +1 because we want the index after the split
        separate_saccade_idxs = np.split(saccade_candidate_idxs, splitting_idxs)

        # exclude saccades that are shorter than the minimum duration
        saccades_start_end = list(map(lambda sac_idxs: (sac_idxs.min(), sac_idxs.max()), separate_saccade_idxs))
        saccades_start_end = list(
            filter(lambda sac: sac[1] - sac[0] >= self._min_samples_within_event, saccades_start_end))
        return saccades_start_end
