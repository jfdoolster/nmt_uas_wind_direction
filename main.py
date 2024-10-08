
if __name__ == "__main__":

    import pandas as pd
    import matplotlib.pyplot as plt
    from wind_calc import calculate_density, calculate_vector_winds, calculate_vector_winds_error
    from wind_plotter import wind_adjustment_plotter

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d',  '--display' , default=True, action=argparse.BooleanOptionalAction, help='display module figures')
    parser.add_argument('-f', '--file', required=True, type=str,
        help='path to merged csv datafile with measured trisonica and UAV positional data')
    args = parser.parse_args()
    argdict = vars(args)

    displayfigs=argdict['display']
    rawdata_path = argdict['file']

    level0 = pd.read_csv(rawdata_path, parse_dates=['Timestamp', 'TS'])

    df_out = calculate_density(level0)
    df_out = calculate_vector_winds(df_out, uav_heading=True)
    df_out = calculate_vector_winds_error(df_out, uav_heading=True)

    pd.set_option('display.precision', 2)
    print(df_out[['Timestamp','Seconds','T','P','Rho','Rho_err', \
        'Sc','WD','U','U_err','V','V_err','W']])

    wind_adjustment_plotter(df_out)

    if displayfigs: plt.show()

