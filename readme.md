Minimal working example of NMT UAS wind correction routine

developed and tested with python 3.11

### usage

```bash
python ./main.py -f /path/to/file

#example dataset:
python ./main.py -f ./data/merge.csv
```

### output

pandas dataframe with
* original data timestamp ('Timestamp')
* seconds into dataset ('Seconds')
* Temperature ('T') in Celsius
* Pressure ('P') in hPa
* Density ('Rho') in kg/m^3
* 1-Sec averaged vector winds ('U_avg', 'V_avg', 'W_avg') in m/s
* 1-Sec averaged *horizontal* vector winds error ('U_avg_err', 'V_avg_err') in m/s
* 1-Sec averaged horizontal wind speed ('Sc_avg')
* 1-Sec averaged horizontal wind direction ('WD_avg')
* UAS transect normal vector components ('Nx', 'Ny')
* UAS cross wind along transect normal vector and error ('cross_wind', 'cross_wind_err') in m/s

### contact:

jonathan.dooley@student.nmt.edu