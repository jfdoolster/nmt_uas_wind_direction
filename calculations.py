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

def wrap_wind_dir(u: np.ndarray, v:np.ndarray, wrap_factor=2.0) -> (np.ndarray, np.ndarray):
    # http://colaweb.gmu.edu/dev/clim301/lectures/wind/wind-uv
    ws = np.sqrt(u**2 + v**2) # m/s
    wd = np.arctan2(v, u) * 180.0/np.pi # rads
    for i,_ in enumerate(wd):
        while wd[i] > (wrap_factor*360.0):
            wd[i] -= 360.0
        if wd[i] <= (0.0):
            wd[i] += 360.0
    return ws, wd

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

    s_actual, wd_actual = wrap_wind_dir(u_actual, v_actual)

    df_out['Vr']  = v_rotated
    df_out['Ur']  = u_rotated
    df_out['Wr']  = w_rotated

    df_out['Sc'] = s_actual # horizontal, compare with 'S'
    df_out['V']  = v_actual
    df_out['U']  = u_actual
    df_out['W']  = w_actual
    df_out['WD'] = wd_actual

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

def average_wrt_aeris(df_in: pd.DataFrame) -> pd.DataFrame:
    df_out = df_in.copy()

    avg_keys = ['Sc', 'WD', 'V', 'U', 'W', 'U_err', 'V_err']
    for key in avg_keys:
        df_out.loc[:, f"{key}_avg"] = np.nan

    for idx in df_in[df_in['CH4'].notnull()].index:
        for key in avg_keys:
            df_out.loc[:, f"{key}_avg"] = df_in.loc[idx-2:idx+2, key].mean()

    return df_out

def calculate_crosswind_dataframe(df_in: pd.DataFrame) -> pd.DataFrame:
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

