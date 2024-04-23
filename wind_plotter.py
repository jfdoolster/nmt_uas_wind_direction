import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import wind_utils as utils
import wind_consts as consts

def set_x_axis(df_in: pd.DataFrame, ts_value: str) -> np.ndarray:
    x_axis = df_in.index
    if ts_value not in df_in.columns:
        print(f"WARN:\tUnknown key '{ts_value}', defaulting to dataframe index labels")
    else:
        x_axis = df_in[ts_value]

    return x_axis

def wind_adjustment_plotter(df_in: pd.DataFrame, title="", ts_value='Timestamp',
                highlight_ground=True, hightlight_label='__nolabel__') -> plt.Figure:
    plt.rcParams['axes.grid'] = True
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['legend.loc'] = "upper left"
    plt.rc('font', size=14)
    plt.rc('axes', titlesize=20)
    plt.rc('axes', labelsize=14)
    plt.rc('xtick', labelsize=12)
    plt.rc('ytick', labelsize=12)
    plt.rc('legend', fontsize=14)
    plt.rc('figure', titlesize=20)

    plot_num = 2
    fig, axs = plt.subplots(plot_num,1, sharex=True, sharey=True)
    fig.set_figheight(4.5)
    fig.set_figwidth(10)

    xdata = set_x_axis(df_in, ts_value)

    axs[0].plot(xdata, df_in["Vm"], color="C0", label=r"$u_{m}$")
    axs[0].plot(xdata, df_in["Um"], color="C1", label=r"$v_{m}$")
    axs[0].plot(xdata, df_in["S"], color="C2", label=r"$|\vec{u}_{m}|$")
    axs[0].set_title(title)

    df1 = df_in.copy()
    mask = (df_in['V'].isna() & df_in['Vm'].notna()) | \
        (df_in['U'].isna() & df_in['Um'].notna())
    df1.loc[mask, 'V'] = df_in.loc[mask, 'Vm']
    df1.loc[mask, 'U'] = df_in.loc[mask, 'Um']
    WS,_ = utils.wrap_wind_dir(df1['U'], df1['V'])

    axs[1].plot(xdata, df1["V"], color="C0", label=r"$u$")
    axs[1].plot(xdata, df1["U"], color="C1", label=r"$v$")
    axs[1].plot(xdata, WS, color="C2", label=r"$|\vec{u}|$")

    if highlight_ground and ("Sts" in df_in.columns):
        flight_df = df_in[df_in["Sts"] > 0]
        if len(flight_df) > 0:
            flight_start_idx, flight_end_idx = flight_df.index.min(), flight_df.index.max()
            ground_pre  = df_in.iloc[df_in.index.min() : flight_start_idx]
            ground_post = df_in.iloc[flight_end_idx+1 : df_in.index.max()+1]

            for ax in axs:
                if len(ground_pre) > 0:
                    ax.axvspan(min(ground_pre[ts_value]), max(ground_pre[ts_value]), facecolor='grey', alpha=0.2, zorder=3, label=hightlight_label)
                if len(ground_post) > 0:
                    ax.axvspan(min(ground_post[ts_value]), max(ground_post[ts_value]), facecolor='grey', alpha=0.2, zorder=3, label='__nolabel__')

    fig.supylabel("Windspeed (m/s)")
    axs[0].set_ylabel("Measured")
    axs[1].set_ylabel("Adjusted")


    for ax in axs: # pylint: disable=invalid-name
        #ax.legend()
        if ts_value == "Timestamp":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.tick_params(axis="x", labelrotation=45, labelsize=8)
        elif ts_value.lower() == "seconds":
            ax.set_xlabel('Seconds')

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, [consts.U_COMP, consts.V_COMP, consts.WS_MAG, hightlight_label],
                loc='upper left', bbox_to_anchor=(0.13, 0.66))
    fig.tight_layout()
    fig.subplots_adjust(
        hspace=0.000,
    )
    return fig
