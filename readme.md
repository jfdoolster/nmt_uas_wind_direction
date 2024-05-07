Minimal working example of NMT UAS wind correction routine

Developed and tested with python 3.11

### Usage

```bash
python ./main.py -f /path/to/file

#example dataset:
python ./main.py -f ./data/level0.csv
```

### Input

CSV file with the following headers (at least):
* Data timestamp (`'Timestamp'`)
* Measured vector winds (`'Um'`, `'Vm'`, `'Wm'`) in m/s
* Measured vehicle velocity (`'Vx'`, `'Vy'`, `'Vz'`) in m/s
    * assuming East-North-Up coordinate system (`+'Vx'` moving East, `+'Vy'` moving North, `+'Vz'` increasing in altitude)
    * **May not be default coordinate system from Vehicle/UAV**
* Temperature (`'T'`) in Celsius
* Pressure (`'P'`) in hPa
* Anemometer Compass heading, Mag. Direction, (`'MD'`) in degrees
* Vehicle/UAV heading (`'Yaw'`) in degrees (optional, but recommended)

Program automatically used vehicle heading (`'Yaw'`) is available.
To use `'MD'` from TWS, don't include `'Yaw'` in input csv and/or set `uav_heading=False` in `calculate_vector_winds()` and `calculate_vector_winds_error()` (see [`main.py`](./main.py) and [`wind_calc.py`](./wind_calc.py)).

### Output

pandas dataframe with
* original data timestamp (`'Timestamp'`)
* seconds into dataset (`'Seconds'`)
* Temperature (`'T'`) in Celsius
* Pressure (`'P'`) in hPa
* Density (`'Rho'`) in kg/m^3
* 1-Sec averaged vector winds (`'U_avg'`, `'V_avg'`, `'W_avg'`) in m/s
* 1-Sec averaged *horizontal* vector winds error (`'U_avg_err'`, `'V_avg_err'`) in m/s
* 1-Sec averaged horizontal wind speed (`'Sc_avg'`)
* 1-Sec averaged horizontal wind direction (`'WD_avg'`)
* UAS transect normal vector components (`'Nx'`, `'Ny'`)
* UAS cross wind along transect normal vector and error (`'cross_wind'`, `'cross_wind_err'`) in m/s

### Contact:

jonathan.dooley@student.nmt.edu