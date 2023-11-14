import pandas as pd
from calculations import calculate_density, calculate_vector_winds, calculate_vector_winds_error


def calculations_on_merged_df(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = calculate_density(df_in)
    df_out = calculate_vector_winds(df_out)
    df_out = calculate_vector_winds_error(df_out)

    return df_out

if __name__ == "__main__":

    merge = pd.read_csv('data/20230419-Flight0/merge.csv')

    out = calculations_on_merged_df(merge)

    display = out[['Timestamp', 'Rho', 'Rho_err', 'S', 'Um', 'Vm', 'Wm', \
            'Ur', 'Vr', 'Wr', 'Sc', 'U', 'V', 'W', 'U_err', 'V_err']]

    print(display)

