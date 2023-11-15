import pandas as pd
from custom_plotter import plot_wind_correction
from calculations import calculate_density, calculate_vector_winds, \
    calculate_vector_winds_error, average_wrt_aeris, calculate_crosswind_dataframe

def calculations_on_merged_df(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = calculate_density(df_in)
    df_out = calculate_vector_winds(df_out)
    df_out = calculate_vector_winds_error(df_out)
    df_out = average_wrt_aeris(df_out)

    return df_out

if __name__ == "__main__":

    import argparse
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, type=str,
        help='path to merged csv datafile with measured trisonica and UAV positional data')
    args = parser.parse_args()
    argdict = vars(args)

    rawdata_path = argdict['file']

    merge = pd.read_csv(rawdata_path, parse_dates=['Timestamp', 'TS'])

    out = calculations_on_merged_df(merge)
    final = calculate_crosswind_dataframe(out)

    pd.set_option('display.precision', 2)
    print(final[['Timestamp','Seconds','T','P','Rho', \
        'Sc_avg','WD_avg','U_avg','V_avg','W_avg','U_err_avg','V_err_avg', \
            'Nx', 'Ny', 'cross_wind', 'cross_wind_err']])

    plot_wind_correction(out)
    plt.show()

