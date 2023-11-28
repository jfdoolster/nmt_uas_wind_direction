import pandas as pd

if __name__ == "__main__":
    from wind_calc import calculations_on_merged_df, calculate_crosswind_dataframe
    from wind_plotter import wind_correction_plotter

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

    wind_correction_plotter(out)
    plt.show()

