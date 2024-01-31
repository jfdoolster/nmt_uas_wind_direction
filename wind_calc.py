import pandas as pd
import numpy as np

from wind_consts import *
from wind_utils import *

def calculations_on_merged_df(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = calculate_density(df_in)
    df_out = calculate_vector_winds(df_out)
    df_out = calculate_vector_winds_error(df_out)
    df_out = average_wrt_aeris(df_out)

    return df_out

def calculate_density(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()

    m_air = MM_AIR * 10**-3 # kg/mol
    pressure    = df_in["P"] * 100      # Pa
    temperature = df_in["T"] + 273.15   # K

    rho     = (m_air / gas_constant) * (pressure / temperature) # kg/m^3
    rho_err = (m_air / gas_constant) * np.sqrt(\
        (ERR_TRISONICA_P/temperature)**2 +
        (pressure * ERR_TRISONICA_T/ temperature**2)**2
    ) # kg/m^3

    df_out["Rho"] = rho  # kg/m^3
    df_out["Rho_err"] = rho_err  # kg/m^3

    return df_out

def calc_matching_reference_frames(df_in: pd.DataFrame):
    df_out = df_in.copy()
    df_out["Vx"] =  df_in["Vy"]
    df_out["Vy"] =  df_in["Vx"]
    df_out["Vz"] = -df_in["Vz"]
    return df_out

def calculate_vector_winds(df_in: pd.DataFrame, using_dji_yaw=True) -> pd.DataFrame:
    df_out = df_in.copy()

    #phi = df_in['MD']  * np.pi/180.0 # radians
    #if using_dji_yaw and ('Yaw' in df_in.columns):
    #if using_dji_yaw:
    phi = df_in['Yaw'] * np.pi/180.0 # radians

    u_rotated =  df_in['Um'] * np.cos(phi) + df_in['Vm'] * np.sin(phi) # m/s
    v_rotated = -df_in['Um'] * np.sin(phi) + df_in['Vm'] * np.cos(phi) # m/s
    w_rotated =  df_in['Wm'] # m/s, not actually rotated due to sensor noise

    u_static = u_rotated + df_in['Vx'] # m/s
    v_static = v_rotated + df_in['Vy'] # m/s
    w_static = w_rotated + df_in['Vz'] # m/s

    s_static, wd_static = wrap_wind_dir(u_static, v_static) # m/s, deg

    df_out['Vr']  = v_rotated # m/s
    df_out['Ur']  = u_rotated # m/s
    df_out['Wr']  = w_rotated # m/s

    df_out['Sc'] = s_static # m/s, horizontal (compare with 'S')
    df_out['V']  = v_static # m/s
    df_out['U']  = u_static # m/s
    df_out['W']  = w_static # m/s
    df_out['WD'] = wd_static # m/s

    return df_out


def calculate_vector_winds_error(df_in: pd.DataFrame, using_dji_yaw=True) -> pd.DataFrame:
    df_out = df_in.copy()

    phi = df_in['MD']  * np.pi/180.0 # rads
    ERR_PHI = ERR_TRISONICA_PHI    # rads
    if using_dji_yaw and ('Yaw' in df_in.columns):
        phi = df_in['Yaw'] * np.pi/180.0 # rads
        ERR_PHI = ERR_M600P_PHI        # rads

        du_dum  = np.cos(phi) + np.sin(phi)
        du_dphi = -df_in['Um'] * np.sin(phi) + df_in['Vm'] * np.cos(phi)
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

def average_wrt_aeris(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()

    avg_keys = ['Sc', 'WD', 'V', 'U', 'W', 'U_err', 'V_err']
    for key in avg_keys:
        df_out.loc[:, f"{key}_avg"] = np.nan

    for idx in df_in[df_in['CH4'].notnull()].index:
        for key in avg_keys:
            # todo: indexes may not be in order?
            df_out.loc[idx, f"{key}_avg"] = df_in.loc[idx-2:idx+2, key].mean()

    return df_out

def filter_payload_nulls(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()
    df_out.dropna(subset=['CH4','C2H6'], inplace=True)
    return df_out

def calculate_crosswind_dataframe(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()
    df_out['Nx'], df_out['Ny'] = normal_vector(df_out['Vx'], df_out['Vy'])

    x_wind = df_out["U_avg"]*df_out["Nx"] + df_out["V_avg"]*df_out["Ny"] # m/s

    uerr = df_out["U_err_avg"] * df_out["Nx"] # m/s
    verr = df_out["V_err_avg"] * df_out["Ny"] # m/s

    nxerr = df_out["U_avg"] * 0.0 # kayrds
    nyerr = df_out["V_avg"] * 0.0 # kayrds

    x_wind_err = np.sqrt((df_out['Nx']**2 * uerr**2) + (df_out['Ny']**2 * verr**2)
                         + (df_out['U_avg']**2 * nxerr**2) + (df_out['V_avg']**2 * nyerr**2)) # m/s

    df_out["cross_wind"]     = x_wind # m/s
    df_out["cross_wind_err"] = x_wind_err # m/s

    df_out.drop(columns=['S','Um','Vm','Wm','Vr','Ur','Wr','Sc','V','U','W','WD','V_err','U_err'], inplace=True)
    df_out.reset_index(drop=True, inplace=True)
    df_out['Seconds'] -= df_out['Seconds'].min() # s (start at zero)
    return df_out

def normal_vector(Vx: np.array, Vy: np.array):
    Nx = []
    Ny = []
    for vx, vy in zip(Vx, Vy):
        if (vy != 0.0) & (vy != np.nan):
            nx1,_ = quadratic_equ(a=((vx/vy)**2 + 1), b=0, c=-1)
            nx = abs(nx1)
            ny = np.sqrt(1 - nx**2)

        elif (vx != 0.0) & (vx != np.nan):
            ny1,_ = quadratic_equ(a=((vy/vx)**2 + 1), b=0, c=-1)
            ny = abs(ny1)
            nx = np.sqrt(1 - ny**2)
        else:
            nx, ny = np.nan, np.nan

        if (vx > 0.0) & (vy > 0.0): # Q1
            ny = -ny # n = Q2
        elif (vx < 0.0) & (vy < 0.0): # Q3
            ny = -ny # n = Q2

        Nx.append(nx)
        Ny.append(ny)

    return np.array(Nx), np.array(Ny)

def quadratic_equ(a: float,b: float,c: float): # pylint: disable=invalid-name
    """
    solve for roots of quadratic equation with constants a, b, c
    """
    d = b**2 - 4 * a * c # pylint: disable=invalid-name

    num1 = -b + np.sqrt(d)
    num2 = -b - np.sqrt(d)
    den  =  2 * a

    root1 = num1 / den
    root2 = num2 / den

    return root1, root2

