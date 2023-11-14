import pandas as pd
import numpy as np
from calculations import calculate_density, calculate_vector_winds, \
    calculate_vector_winds_error, normal_vector


def average_wrt_aeris(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()

    avg_keys = ['Sc', 'WD', 'V', 'U', 'W', 'U_err', 'V_err']
    for key in avg_keys:
        df_out.loc[:, f"{key}_avg"] = np.nan

    for idx in df_in[df_in['CH4'].notnull()].index:
        for key in avg_keys:
            df_out.loc[:, f"{key}_avg"] = df_in.loc[idx-2:idx+2, key].mean()

    return df_out

def calculate_averge_dataframe(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()
    df_out.dropna(subset=['CH4','C2H6'], inplace=True)
    df_out['Nx'], df_out['Ny'] = normal_vector(df_out['Vx'], df_out['Vy'])

    x_wind = df_out["V_avg"]*df_out["Nx"] + df_out["U_avg"]*df_out["Ny"]

    uerr = df_out["U_err_avg"] * df_out["Ny"]
    verr = df_out["V_err_avg"] * df_out["Nx"]

    nxerr = df_out["V_avg"] * 0.0
    nyerr = df_out["V_avg"] * 0.0

    x_wind_err = np.sqrt(uerr**2 + verr**2 + nxerr**2 + nyerr**2)

    df_out["cross_wind"]     = x_wind
    df_out["cross_wind_err"] = x_wind_err

    df_out.drop(columns=['S','Um','Vm','Wm','Vr','Ur','Wr','Sc','V','U','W','WD','V_err','U_err'], inplace=True)
    df_out.reset_index(drop=True, inplace=True)
    df_out['Seconds'] -= df_out.loc[0,'Seconds']
    return df_out

def calculations_on_merged_df(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = calculate_density(df_in)
    df_out = calculate_vector_winds(df_out)
    df_out = calculate_vector_winds_error(df_out)
    df_out = average_wrt_aeris(df_out)
    df_avg = calculate_averge_dataframe(df_out)

    return df_avg

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, type=str,
        help='path to merged csv datafile with measured trisonica and UAV positional data')
    args = parser.parse_args()
    argdict = vars(args)

    rawdata_path = argdict['file']

    merge = pd.read_csv(rawdata_path)

    out = calculations_on_merged_df(merge)

    print(out[['Timestamp','Seconds','T','P','Rho', \
        'Sc_avg','WD_avg','U_avg','V_avg','W_avg','U_err_avg','V_err_avg', \
            'Nx', 'Ny', 'cross_wind', 'cross_wind_err']])

