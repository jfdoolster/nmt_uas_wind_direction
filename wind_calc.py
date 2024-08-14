import pandas as pd
import numpy as np

import wind_consts as consts
import wind_utils as utils

def calculate_density(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()

    m_air = consts.MM_AIR * 10**-3 # kg/mol
    pressure    = df_in["P"] * 100      # Pa
    temperature = df_in["T"] + 273.15   # K

    rho     = (m_air / consts.gas_constant) * (pressure / temperature) # kg/m^3
    rho_err = (m_air / consts.gas_constant) * np.sqrt(\
        (consts.ERR_TRISONICA_P/temperature)**2 +
        (pressure * consts.ERR_TRISONICA_T/ temperature**2)**2
    ) # kg/m^3

    df_out["Rho"] = rho  # kg/m^3
    df_out["Rho_err"] = rho_err  # kg/m^3

    return df_out


def calculate_vector_winds(df_in: pd.DataFrame, uav_heading=True) -> pd.DataFrame:
    df_out = df_in.copy()

    phi = df_in['MD']  * np.pi/180.0 # radians
    if uav_heading and ('Yaw' in df_in.columns):
        phi = df_in['Yaw'] * np.pi/180.0 # radians

    u_rotated =  df_in['Um'] * np.cos(phi) + df_in['Vm'] * np.sin(phi) # m/s
    v_rotated = -df_in['Um'] * np.sin(phi) + df_in['Vm'] * np.cos(phi) # m/s
    w_rotated =  df_in['Wm'] # m/s, not actually rotated due to sensor noise

    u_static = u_rotated + df_in['Vx'] # m/s
    v_static = v_rotated + df_in['Vy'] # m/s
    w_static = w_rotated + df_in['Vz'] # m/s

    s_static, wd_static = utils.wrap_wind_dir(u_static, v_static) # m/s, deg

    df_out['Vr']  = v_rotated # m/s
    df_out['Ur']  = u_rotated # m/s
    df_out['Wr']  = w_rotated # m/s

    df_out['Sc'] = s_static # m/s, horizontal (compare with 'S')
    df_out['V']  = v_static # m/s
    df_out['U']  = u_static # m/s
    df_out['W']  = w_static # m/s
    df_out['WD'] = wd_static # m/s

    return df_out


def calculate_vector_winds_error(df_in: pd.DataFrame, uav_heading=True) -> pd.DataFrame:
    df_out = df_in.copy()

    phi = df_in['MD']  * np.pi/180.0 # rads
    ERR_PHI = consts.ERR_TRISONICA_PHI    # rads
    if uav_heading and ('Yaw' in df_in.columns):
        phi = df_in['Yaw'] * np.pi/180.0 # rads
        ERR_PHI = consts.ERR_M600P_PHI        # rads

        du_dum  = np.cos(phi)
        du_dphi = (df_in['Vm'] * np.cos(phi) - df_in['Um'] * np.sin(phi))
        du_dv   = 1

        u_error = np.sqrt(
                (du_dum)**2 * consts.ERR_TRISONICA_UM**2 + \
                (du_dphi)**2 * ERR_PHI**2 + \
                (du_dv)**2 * consts.ERR_M600P_VY**2 )

        dv_dvm  = np.cos(phi)
        dv_dphi = -(df_in['Vm'] * np.sin(phi) + df_in['Um'] * np.cos(phi))
        dv_dv   = 1

        v_error = np.sqrt(
                (dv_dvm)**2 * consts.ERR_TRISONICA_VM**2 + \
                (dv_dphi)**2 * ERR_PHI**2 + \
                (dv_dv)**2 * consts.ERR_M600P_VX**2 )

        df_out['V_err'] = v_error
        df_out['U_err'] = u_error

        return df_out