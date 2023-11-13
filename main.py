import pandas as pd
import numpy as np
from calculations import calculate_density, calculate_vector_winds, calculate_vector_winds_error


if __name__ == "__main__":

    merge = pd.read_csv('data/20230419-Flight0/merge.csv')

    out = calculate_density(merge)
    out = calculate_vector_winds(out)
    out = calculate_vector_winds_error(out)

    display = out[['Timestamp', 'Rho', 'Rho_err', 'S', 'Um', 'Vm', 'Wm', \
            'Ur', 'Vr', 'Wr', 'Sc', 'U', 'V', 'W', 'U_err', 'V_err']]

    print(display)

