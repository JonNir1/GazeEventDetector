import os
import numpy as np
import cv2
from typing import Tuple

import constants as cnst
import experiment_config as cnfg
from Utils.ScreenMonitor import ScreenMonitor
from LWS.DataModels.LWSTrial import LWSTrial
from LWS.DataModels.LWSFixationEvent import LWSFixationEvent


class LWSVisualizer:
    FILE_SUFFIX = 'mp4'
    FOURCC = cv2.VideoWriter_fourcc(*'mp4v')

    def __init__(self, screen_monitor: ScreenMonitor = None):
        self.screen_monitor = ScreenMonitor.from_config() if screen_monitor is None else screen_monitor

    def visualize(self, trial: LWSTrial, output_directory: str = cnfg.OUTPUT_DIR,
                  display_gaze: bool = True, display_fixations: bool = True, show=False, **kwargs):
        """
        Generates a video visualization of the eye-tracking data and behavioral events for the given LWSTrial.
        This video is saved to the path `output_directory/subject_id/trial_id.mp4`.

        :param trial: The LWSTrial object containing the raw eye-tracking data, the gaze events and behavioral data (triggers).
        :param output_directory: The directory where the generated video will be saved. If not specified, the default directory is used.
        :param display_gaze: Whether to display the gaze circles. Defaults to True.
        :param display_fixations: Whether to display the fixations. Defaults to True.
        :param show: Whether to show the video after generating it. Defaults to False.
        :param kwargs: Additional keyword arguments for customizing the visualization parameters.

        keyword arguments:
            Trigger Visualization:
            - target_radius (int): The radius of the target circle in pixels. Defaults to 25.
            - target_edge_size (int): The width of the target circle's edge in pixels. Defaults to 4.
            - marked_target_color (Tuple[int, int, int]): The color of the marked target circle in BGR format. Defaults to (0, 0, 0) (black).
            - confirmed_target_color (Tuple[int, int, int]): The color of the confirmed target circle in BGR format. Defaults to (50, 150, 50) (dark green).
            Gaze Visualization:
            - gaze_radius (int): The radius of the gaze circle in pixels. Defaults to 10.
            - gaze_color (Tuple[int, int, int]): The color of the gaze circle in BGR format. Defaults to (255, 200, 100) (light-blue).
            Fixation Visualization:
            - fixation_radius (int/None): The radius of the fixation circle in pixels. If None, the fixation will be
                    displayed as an ellipse with axes lengths of 2*std_x and 2*std_y. Defaults to None.
            - fixation_color (Tuple[int, int, int]): The color of the fixation circle in BGR format. Defaults to (40, 140, 255) (orange).
            - fixation_alpha (float): The opacity of the fixation circle. Defaults to 0.5.

        No return value
        """
        save_path = self.__get_video_full_path(output_directory, trial.get_subject_info().subject_id, trial.trial_num)

        # get raw behavioral data
        timestamps, x, y = trial.get_raw_gaze_coordinates(eye='dominant')
        triggers = trial.get_behavioral_data().get('trigger').values
        num_samples = len(timestamps)

        # prepare visual inputs
        fps = round(trial.sampling_rate)
        resolution = self.screen_monitor.resolution
        bg_img = trial.get_stimulus().get_image(color_format='BGR')
        bg_img = cv2.resize(bg_img, resolution)
        prev_bg_img = bg_img.copy()  # used to enable reverting to previous bg image if subject's action is undone
        circle_center = np.array([np.nan, np.nan])  # to draw a circle around the target

        # extract keyword arguments
        target_radius = kwargs.get('target_radius', 35)
        target_edge_size = kwargs.get('target_edge_size', 4)
        marked_target_color: Tuple[int, int, int] = kwargs.get('marked_target_color', (0, 0, 0))            # default: black
        confirmed_target_color: Tuple[int, int, int] = kwargs.get('confirmed_target_color', (50, 150, 50))  # default: dark green
        gaze_radius = kwargs.get('gaze_radius', 10)
        gaze_color: Tuple[int, int, int] = kwargs.get('gaze_color', (255, 200, 100))                        # default: light-blue
        fixation_radius = kwargs.get('fixation_radius', None)  # default: use fixation event's radius
        fixation_color: Tuple[int, int, int] = kwargs.get('fixation_color', (40, 140, 255))                  # default: orange
        fixation_alpha = kwargs.get('fixation_alpha', 0.5)

        video_writer = cv2.VideoWriter(save_path, self.FOURCC, fps, resolution)
        for i in range(num_samples):
            # get current sample data
            curr_x = int(x[i]) if not np.isnan(x[i]) else None
            curr_y = int(y[i]) if not np.isnan(y[i]) else None
            curr_trigger = int(triggers[i]) if not np.isnan(triggers[i]) else None

            # if there is a current trigger, draw it and keep it for future frames
            if curr_trigger is not None:
                if curr_trigger == cnfg.MARK_TARGET_SUCCESSFUL_TRIGGER:
                    # draw a circle around the marked target in future frames until action is confirmed/rejected
                    cv2.circle(bg_img, (curr_x, curr_y), target_radius, marked_target_color, target_edge_size)
                    circle_center = np.array([curr_x, curr_y])  # store for confirmation frame

                elif curr_trigger == cnfg.CONFIRM_TARGET_SUCCESSFUL_TRIGGER:
                    # draw a circle around the marked target in all future frames
                    cv2.circle(bg_img, circle_center, target_radius, confirmed_target_color, target_edge_size)
                    prev_bg_img = bg_img.copy()  # write over the prev_bg_img to make sure the circle stays in future frames

                elif curr_trigger == cnfg.REJECT_TARGET_SUCCESSFUL_TRIGGER:
                    # revert to previous bg image
                    bg_img = prev_bg_img.copy()

            # draw current gaze data on the frame
            gaze_img = bg_img.copy()
            if display_gaze and (curr_x is not None) and (curr_y is not None):
                cv2.circle(gaze_img, (curr_x, curr_y), gaze_radius, gaze_color, -1)

            # draw the current fixation on the frame if it exists
            fix_img = gaze_img.copy()
            if display_fixations:
                curr_t = timestamps[i]
                fixations = trial.get_gaze_events(cnst.FIXATION)
                current_fixations = list(filter(lambda f: f.start_time <= curr_t <= f.end_time, fixations))
                if len(current_fixations) > 0:
                    curr_fix = current_fixations[0].__class__ = LWSFixationEvent
                    x, y = curr_fix.center_of_mass
                    fix_w, fix_h = curr_fix.std if fixation_radius is None else fixation_radius / 2, fixation_radius / 2
                    cv2.ellipse(fix_img, (int(x), int(y)), (int(fix_w), int(fix_h)), 0, 0, 360, fixation_color, -1)

            # create a combined image of the gaze and fixation images and write it to the video
            final_img = cv2.addWeighted(fix_img, fixation_alpha, gaze_img, 1 - fixation_alpha, 0)
            video_writer.write(final_img)
        video_writer.release()

        if show:
            self.display_video(trial.get_subject_info().subject_id, trial.trial_num, output_directory)

    def display_video(self, subject_id: int, trial_num: int, output_directory: str = cnfg.OUTPUT_DIR):
        """
        Displays a video generated by `visualize` for the given subject and trial.
        Implementation adapted from https://tinyurl.com/cv2tutorial

        :raises FileNotFoundError: If the video file is not found at the given path.
        """
        video_path = self.__get_video_full_path(output_directory, subject_id, trial_num)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f'Video file not found at {video_path}')

        window_name = f"LWS S{subject_id} T{trial_num}"
        video = cv2.VideoCapture(video_path)
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video.release()
        cv2.destroyAllWindows()

    @staticmethod
    def __get_video_full_path(output_directory: str, subject_id: int, trial_num: int):
        subject_dir = os.path.join(output_directory, f'S{subject_id}')
        if not os.path.exists(subject_dir):
            os.makedirs(subject_dir)
        subject_video_dir = os.path.join(subject_dir, 'videos')
        if not os.path.exists(subject_video_dir):
            os.makedirs(subject_video_dir)
        output_filename = f'T{trial_num:03d}.{LWSVisualizer.FILE_SUFFIX}'
        return os.path.join(subject_video_dir, output_filename)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    def __str__(self) -> str:
        return self.__repr__()
