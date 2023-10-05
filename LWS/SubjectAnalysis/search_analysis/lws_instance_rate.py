import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from LWS.DataModels.LWSSubject import LWSSubject
from LWS.DataModels.LWSArrayStimulus import LWSStimulusTypeEnum
import Visualization.visualization_utils as visutils
import LWS.SubjectAnalysis.search_analysis.identify_lws_instances as identify_lws


def lws_rates_figure(subject: LWSSubject,
                     proximity_thresholds: np.ndarray,
                     time_difference_thresholds: np.ndarray) -> plt.Figure:
    """
    Plot the LWS rate for each stimulus type as a function of proximity threshold.
    """
    nrows, ncols = 2, len(time_difference_thresholds)
    fig = visutils.set_figure_properties(fig=None, figsize=(27, 15), tight_layout=True,
                                         title=f"LWS Rate for Varying Stimulus Types\n" +
                                               "(top: out of all fixations\n" +
                                               "bottom: out of target-proximal fixations)",
                                         title_height=0.98)

    for col, td in enumerate(time_difference_thresholds):
        bottom_ax = fig.add_subplot(nrows, ncols, ncols + col + 1)
        bottom_ax = _draw_lws_rates(bottom_ax, subject, proximity_thresholds, td, proximal_fixations_only=True)

        top_ax = fig.add_subplot(nrows, ncols, col + 1, sharex=bottom_ax)
        top_ax = _draw_lws_rates(top_ax, subject, proximity_thresholds, td, proximal_fixations_only=False)
    return fig


def _draw_lws_rates(ax: plt.Axes,
                    subject: LWSSubject,
                    proximity_thresholds: np.ndarray,
                    time_difference_threshold: float,
                    proximal_fixations_only: bool) -> plt.Axes:
    # load the LWS rate dataframe:
    df_name = identify_lws.RATES_DF_BASE_NAME + ("_proximal_fixations" if proximal_fixations_only else "_all_fixations")
    df_path = subject.get_dataframe_path(df_name)
    try:
        lws_rate_df = pd.read_pickle(df_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find LWS rate dataframe at {df_path}")

    # extract mean of lws rate for each stimulus type:
    data_labels = ["all"] + [f"{stim_type}" for stim_type in LWSStimulusTypeEnum]
    mean_rates = np.zeros((len(data_labels), len(proximity_thresholds)))
    mean_rates[0] = lws_rate_df.mean(axis=0)
    for i, st in enumerate(LWSStimulusTypeEnum):
        stim_type_trials = list(filter(lambda tr: tr.stim_type == st, lws_rate_df.index))
        mean_rates[i + 1] = lws_rate_df.loc[stim_type_trials].mean(axis=0)

    visutils.generic_line_chart(ax=ax,
                                data_labels=data_labels,
                                xs=[proximity_thresholds for _ in range(len(data_labels))],
                                ys=[100 * mean_rates[i] for i in range(len(data_labels))])

    ax_title = f"Δt Threshold: {time_difference_threshold:.1f} (ms)" if not proximal_fixations_only else ""
    x_label = "Threshold Visual Angle (°)" if proximal_fixations_only else ""
    visutils.set_axes_properties(ax=ax,
                                 ax_title=ax_title,
                                 xlabel=x_label,
                                 ylabel="LWS Rate (% fixations)",
                                 show_legend=True)
    return ax