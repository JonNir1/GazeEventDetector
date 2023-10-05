import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from LWS.DataModels.LWSSubject import LWSSubject
from LWS.DataModels.LWSArrayStimulus import LWSStimulusTypeEnum
import Visualization.visualization_utils as visutils
import LWS.SubjectAnalysis.search_analysis.identify_lws_instances as identify_lws


def lws_rates_figure(subject: LWSSubject,
                     time_difference_thresholds: np.ndarray) -> plt.Figure:
    """
    Plot the LWS rate for each stimulus type as a function of proximity threshold.
    """
    fig, axes = plt.subplots(nrows=2, ncols=len(time_difference_thresholds),
                             figsize=(27, 15), tight_layout=True,
                             sharex='col', sharey='row')

    for col, td in enumerate(time_difference_thresholds):
        top_ax = _draw_lws_rates(axes[0, col], subject, td, proximal_fixations_only=False)
        bottom_ax = _draw_lws_rates(axes[1, col], subject, td, proximal_fixations_only=True)
        if col == 0:
            top_ax.set_ylabel("LWS Rate (% fixations)")
            bottom_ax.set_ylabel("LWS Rate (% fixations)")

    fig = visutils.set_figure_properties(fig=fig, figsize=(27, 12), tight_layout=True,
                                         title=f"LWS Rate for Varying Stimulus Types\n" +
                                               "(top: out of all fixations\n" +
                                               "bottom: out of target-proximal fixations)",
                                         title_height=0.98)
    return fig


def _draw_lws_rates(ax: plt.Axes,
                    subject: LWSSubject,
                    td_threshold: float,
                    proximal_fixations_only: bool) -> plt.Axes:
    # load the LWS rate dataframe:
    df_name = identify_lws.RATES_DF_BASE_NAME + ("_proximal_fixations" if proximal_fixations_only else "_all_fixations")
    df_path = subject.get_dataframe_path(df_name)
    try:
        lws_rate_df = pd.read_pickle(df_path)
        # filter by time difference threshold:
        lws_rate_df = lws_rate_df.loc[:, lws_rate_df.columns.get_level_values(1) == td_threshold]
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find LWS rate dataframe at {df_path}")
    if lws_rate_df.empty:
        raise KeyError(f"No data for time difference threshold {td_threshold}")

    # extract mean of lws rate for each stimulus type:
    data_labels = ["all"] + [f"{stim_type}" for stim_type in LWSStimulusTypeEnum]
    proximity_thresholds = lws_rate_df.columns.get_level_values(0).values
    mean_rates = np.zeros((len(data_labels), len(proximity_thresholds)))
    mean_rates[0] = lws_rate_df.mean(axis=0)
    for i, st in enumerate(LWSStimulusTypeEnum):
        stim_type_trials = list(filter(lambda tr: tr.stim_type == st, lws_rate_df.index))
        mean_rates[i + 1] = lws_rate_df.loc[stim_type_trials].mean(axis=0)

    visutils.generic_line_chart(ax=ax,
                                data_labels=data_labels,
                                xs=[proximity_thresholds for _ in range(len(data_labels))],
                                ys=[100 * mean_rates[i] for i in range(len(data_labels))])

    ax_title = f"Δt Threshold: {td_threshold:.1f} (ms)" if not proximal_fixations_only else ""
    x_label = "Threshold Visual Angle (°)" if proximal_fixations_only else ""
    visutils.set_axes_properties(ax=ax,
                                 ax_title=ax_title,
                                 xlabel=x_label,
                                 show_legend=True)
    return ax
