import pandas as pd
import numpy as np
from scipy.constants import gas_constant

MM_AIR  = 28.9647 # g/mol
ERR_TRISONICA_P = 1000 # Pa
ERR_TRISONICA_T =    2 # C

ERR_M600P_VX   = 0.05 # m/s
ERR_M600P_VY   = 0.05 # m/s
ERR_M600P_PHI  = 0.05 # rad

ERR_TRISONICA_UM = 200E-3 # m/s
ERR_TRISONICA_VM = 200E-3 # m/s
ERR_TRISONICA_WM = 200E-3 # m/s
ERR_TRISONICA_PHI  = 0.20 # rad

def calculate_density(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()

    m_air = MM_AIR * 10**-3 # kg/mol
    pressure    = df_in["P"] * 100      # Pa
    temperature = df_in["T"] + 273.15   # K

    rho     = (m_air / gas_constant) * (pressure / temperature) # kg/m^3
    rho_err = (m_air / gas_constant) * np.sqrt(\
        (ERR_TRISONICA_P/temperature)**2 +
        (pressure * ERR_TRISONICA_T/ temperature**2)**2
    )

    df_out["Rho"] = rho
    df_out["Rho_err"] = rho_err

    return df_out

def calculate_vector_winds(df_in: pd.DataFrame, using_dji_yaw=True) -> pd.DataFrame:
    df_out = df_in.copy()

    phi = df_in['MD']  * np.pi/180 # radians
    if using_dji_yaw and ('Yaw' in df_in.columns):
        phi = df_in['Yaw'] * np.pi/180 # radians

    u_rotated =  df_in['Um'] * np.cos(phi) + df_in['Vm'] * np.sin(phi) # m/s
    v_rotated = -df_in['Um'] * np.sin(phi) + df_in['Vm'] * np.cos(phi) # m/s
    w_rotated =  df_in['Wm'] # not actually rotated due to sensor noise

    v_actual = v_rotated
    if 'Vx' in df_in.columns:
        v_actual = v_rotated   + df_in['Vx']

    u_actual = u_rotated
    if 'Vy' in df_in.columns:
        u_actual = u_rotated   + df_in['Vy']

    w_actual = w_rotated
    if 'Vz' in df_in.columns:
        w_actual = w_rotated - df_in['Vz']

    df_out['Vr']  = v_rotated
    df_out['Ur']  = u_rotated
    df_out['Wr']  = w_rotated

    df_out['Sc'] = np.sqrt(v_actual**2 + u_actual**2) # horizontal, compare with 'S'
    df_out['V']  = v_actual
    df_out['U']  = u_actual
    df_out['W']  = w_actual

    return df_out


def calculate_vector_winds_error(df_in: pd.DataFrame, using_dji_yaw=True) -> pd.DataFrame:
    df_out = df_in.copy()

    phi = df_in['MD']  * np.pi/180 # rads
    ERR_PHI = ERR_TRISONICA_PHI    # rads
    if using_dji_yaw and ('Yaw' in df_in.columns):
        phi = df_in['Yaw'] * np.pi/180 # rads
        ERR_PHI = ERR_M600P_PHI        # rads

        du_dum  = np.cos(phi) + np.sin(phi)
        du_dphi = -df_in['Um'] * np.sin(phi) + df_in['Um'] * np.cos(phi)
        du_dv   = 1

        u_error = np.sqrt(
                (du_dum)**2 * ERR_TRISONICA_UM**2 + \
                (du_dphi)**2 * ERR_PHI**2 + \
                (du_dv)**2 * ERR_M600P_VY**2 )

        dv_dvm  = -np.sin(phi) + np.cos(phi)
        dv_dphi = -df_in['Vm'] * np.cos(phi) - df_in['Vm'] * np.sin(phi)
        dv_dv   = 1

        v_error = np.sqrt(
                (dv_dvm)**2 * ERR_TRISONICA_VM**2 + \
                (dv_dphi)**2 * ERR_PHI**2 + \
                (dv_dv)**2 * ERR_M600P_VX**2 )

        df_out['V_err'] = v_error
        df_out['U_err'] = u_error

        return df_out
