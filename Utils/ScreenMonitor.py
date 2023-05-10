import numpy as np
from typing import Tuple

import experiment_config as cnfg


class ScreenMonitor:
    """
    Holds information about the computer screen used for the experiments.
    Default values are taken from the experiment_config.py file.
    """

    def __init__(self, width: int, height: int, refresh_rate: float, resolution: Tuple[float, float]):
        self.__width = width
        self.__height = height
        self.__refresh_rate = refresh_rate
        self.__resolution = resolution

    @classmethod
    def from_config(cls):
        return cls(cnfg.SCREEN_WIDTH, cnfg.SCREEN_HEIGHT, cnfg.SCREEN_REFRESH_RATE, cnfg.SCREEN_RESOLUTION)

    @property
    def width(self) -> int:
        # width of the screen in centimeters
        return self.__width

    @property
    def height(self) -> int:
        # height of the screen in centimeters
        return self.__height

    @property
    def refresh_rate(self) -> float:
        # refresh rate of the screen in Hz
        return self.__refresh_rate

    @property
    def resolution(self) -> Tuple[float, float]:
        # resolution of the screen, i.e. number of pixels in width and height
        return self.__resolution

    @property
    def pixel_size(self) -> float:
        # Returns the approximate size of one pixel in centimeters
        diagonal_length = np.sqrt(np.power(self.width, 2) + np.power(self.height, 2))  # size of diagonal in centimeters
        diagonal_pixels = np.sqrt(np.power(self.resolution[0], 2) + np.power(self.resolution[1], 2))  # size of diagonal in pixels
        return diagonal_length / diagonal_pixels
