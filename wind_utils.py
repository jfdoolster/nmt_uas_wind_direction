import numpy as np

def wrap_wind_dir(u: np.ndarray, v:np.ndarray, wrap_factor=2.0) -> (np.ndarray, np.ndarray):
    # http://colaweb.gmu.edu/dev/clim301/lectures/wind/wind-uv
    ws = np.sqrt(u**2 + v**2) # m/s
    wd = 270 - (np.arctan2(v, u) * 180.0/np.pi) # degrees
    for i,_ in enumerate(wd):
        while wd[i] > (wrap_factor*360.0):
            wd[i] -= 360.0
        if wd[i] <= (0.0):
            wd[i] += 360.0
    return ws, wd

