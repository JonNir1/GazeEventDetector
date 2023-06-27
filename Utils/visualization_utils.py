import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

from LWS.DataModels.LWSTrial import LWSTrial


def get_axis_limits(ax: plt.Axes, axis: str) -> Tuple[float, float]:
    """
    Returns the maximun and minimum values among all lines in the given plt.Axes object.

    :raises ValueError: If axis is not 'x' or 'y'.
    """
    axis = axis.lower()
    if axis not in ['x', 'y']:
        raise ValueError(f"Invalid axis '{axis}'! Must be either 'x' or 'y'.")
    axis_idx = 0 if axis == 'x' else 1
    min_val, max_val = float('inf'), float('-inf')
    for ln in ax.lines:
        data = ln.get_data()[axis_idx]
        tmp_min = float(np.min(np.ma.masked_invalid(data)))
        tmp_max = float(np.max(np.ma.masked_invalid(data)))
        min_val = min(min_val, tmp_min)
        max_val = max(max_val, tmp_max)
    return min_val, max_val


def set_axis_properties(ax: plt.Axes, axis: str, label: str, text_size: int) -> plt.Axes:
    """
    Sets the X/Y axis limits, ticks and label of the given plt.Axes object.
    :param ax: The plt.Axes object to set the properties of.
    :param axis: The axis to set the properties of. Must be either 'x' or 'y'.
    :param label: The label to set for the axis.
    :param text_size: The size of the axis label and ticks.

    :raises ValueError: If axis is not 'x' or 'y'.
    """
    axis = axis.lower()
    if axis not in ['x', 'y']:
        raise ValueError(f"Invalid axis '{axis}'! Must be either 'x' or 'y'.")

    _, axis_max = get_axis_limits(ax, axis=axis)
    jumps = 2 * np.power(10, max(0, int(np.log10(axis_max)) - 1))
    if axis == 'x':
        ax.set_xlabel(xlabel=label, fontsize=text_size)
        ax.set_xlimg(bottom=int(-0.02 * axis_max), top=int(1.05 * axis_max))
        xticks = [int(val) for val in np.arange(int(axis_max)) if val % jumps == 0]
        ax.set_xticks(ticks=xticks, labels=[str(tck) for tck in xticks], fontsize=text_size)

    if axis == 'y':
        ax.set_ylabel(ylabel=label, fontsize=text_size)
        ax.set_ylim(bottom=int(-0.02 * axis_max), top=int(1.05 * axis_max))
        yticks = [int(val) for val in np.arange(int(axis_max)) if val % jumps == 0]
        ax.set_yticks(ticks=yticks, labels=[str(tck) for tck in yticks], fontsize=text_size)
    return ax


def set_figure_properties(fig: plt.Figure, ax: plt.Axes, **kwargs):
    """
    Sets the properties of the given figure and axes according to the given keyword arguments:

    Figure Arguments:
        - figsize: the figure's size (width, height) in inches, default is (16, 9).
        - figure_dpi: the figure's DPI, default is 300.
        - title: the figure's title, default is ''.
        - title_size: the size of the title text object in the figure, default is 18.

    Axes Arguments:
        - subtitle: the figure's subtitle, default is ''.
        - subtitle_size: the size of the subtitle text object in the figure, default is 14.
        - show_legend: whether to show the legend or not, default is True.
        - legend_location: the location of the legend in the figure, default is 'lower center'.
        - invert_yaxis: whether to invert the Y axis or not, default is False.

    X-Axis & Y-Axis Arguments:
        - show_axes: whether to show the x,y axes or not, default is True.
        - x_label: the label of the X axis, default is ''.
        - y_label: the label of the Y axis, default is ''.
        - text_size: the size of non-title text objects in the figure, default is 12.

    Returns the figure and axes with the updated properties.
    """
    # general figure properties
    figsize = kwargs.get('figsize', (16, 9))
    fig.set_size_inches(w=figsize[0], h=figsize[1])
    fig.set_dpi(kwargs.get('figure_dpi', 500))
    fig.suptitle(t=kwargs.get('title', ''), fontsize=kwargs.get('title_size', 18), y=0.98)

    # general axes properties
    ax.set_title(label=kwargs.get('subtitle', ''), fontsize=kwargs.get('subtitle_size', 14))
    text_size = kwargs.get('text_size', 12)
    if kwargs.get('show_legend', True):
        ax.legend(loc=kwargs.get('legend_location', 'lower center'), fontsize=text_size)
    if kwargs.get('show_axes', True):
        ax = set_axis_properties(ax=ax, axis='x', label=kwargs.get('x_label', ''), text_size=text_size)
        ax = set_axis_properties(ax=ax, axis='y', label=kwargs.get('y_label', ''), text_size=text_size)

    if kwargs.get('invert_yaxis', False):
        # invert y-axis to match the screen coordinates:
        ax.invert_yaxis()
    return fig, ax