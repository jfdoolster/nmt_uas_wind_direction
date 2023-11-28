import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def set_x_axis(df_in: pd.DataFrame, ts_value: str) -> np.ndarray:
    x_axis = df_in.index
    if ts_value not in df_in.columns:
        print(f"WARN:\tUnknown key '{ts_value}', defaulting to dataframe index labels")
    else:
        x_axis = df_in[ts_value]

    return x_axis

def wind_correction_plotter(df_in: pd.DataFrame, title="", ts_value='Timestamp', highlight_ground=True) -> plt.Figure:

    set_custom_rcparams()
    plot_num = 2
    fig, axs = plt.subplots(plot_num,1, sharex=True, sharey=True)
    fig.suptitle(title)
    fig.set_figheight(5)
    fig.set_figwidth(10)

    xdata = set_x_axis(df_in, ts_value)

    axs[0].plot(xdata, df_in["Vm"], color="C0", label=r"$|\vec{u}_{m}|$")
    axs[0].plot(xdata, df_in["Um"], color="C1", label=r"$|\vec{v}_{m}|$")
    axs[0].plot(xdata, df_in["S"], color="C2", label=r"$|\vec{V}_{w}|$")

    axs[1].plot(xdata, df_in["V"], color="C0", label=r"$|\vec{u}|$")
    axs[1].plot(xdata, df_in["U"], color="C1", label=r"$|\vec{v}|$")
    axs[1].plot(xdata, df_in["Sc"], color="C2", label=r"$|\vec{V}_{w}|$")

    if highlight_ground and ("Sts" in df_in.columns):
        flight_df = df_in[df_in["Sts"] > 0]
        flight_start_idx, flight_end_idx = flight_df.index.min(), flight_df.index.max()
        ground_pre  = df_in.iloc[df_in.index.min() : flight_start_idx]
        ground_post = df_in.iloc[flight_end_idx+1 : df_in.index.max()+1]

        for ax in axs:
            ax.axvspan(min(ground_pre[ts_value]), max(ground_pre[ts_value]), facecolor='grey', alpha=0.2, zorder=3)
            ax.axvspan(min(ground_post[ts_value]), max(ground_post[ts_value]), facecolor='grey', alpha=0.2, zorder=3)

    fig.supylabel("Windspeed (m/s)")
    fs = 11
    axs[0].set_ylabel("Measured", fontsize=fs)
    axs[1].set_ylabel("Corrected", fontsize=fs)

    for ax in axs: # pylint: disable=invalid-name
        ax.legend()
        if ts_value == "Timestamp":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.tick_params(axis="x", labelrotation=45, labelsize=8)
        elif ts_value.lower() == "seconds":
            ax.set_xlabel('Seconds')

    fig.tight_layout()
    return fig


def set_custom_rcparams(grid=True):
    """
    custom rcparams
    """
    plt.rcParams['axes.grid'] = grid
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['legend.loc'] = "upper left"
    # Set the default text font size
    plt.rc('font', size=12)
    # Set the axes title font size
    plt.rc('axes', titlesize=16)
    # Set the axes labels font size
    plt.rc('axes', labelsize=14)
    # Set the font size for x tick labels
    plt.rc('xtick', labelsize=12)
    # Set the font size for y tick labels
    plt.rc('ytick', labelsize=12)
    # Set the legend font size
    plt.rc('legend', fontsize=10)
    # Set the font size of the figure title
    plt.rc('figure', titlesize=16)


