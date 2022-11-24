from utils import getConfigurationByID
import xarray as xr
import numpy as np
from glob import glob
from datetime import datetime
import matplotlib.pyplot as plt
import os
from scipy.interpolate import RegularGridInterpolator
import pickle
import windrose
from sys import argv

def UVtoTgrid(xx, yy, var, xT, yT):
    regrid = RegularGridInterpolator((xx, yy), var, method='linear')
    return regrid([xT, yT])

def openMOOR(file):
    obs = xr.open_dataset(file)
    obs.TIME.values = [datetime.strptime(str(t)[:21], '%Y-%m-%dT%H:%M:%S.%f') for t in obs.TIME.values]
    return obs


def openNEMO(model,depthName):
    ds = xr.open_mfdataset(model, combine='by_coords')
    navlat = ds['nav_lat'].values[ds['nav_lat'].values > 0]
    navlon = ds['nav_lon'].values[ds['nav_lon'].values > 0]
    ds['lat'] = np.unique(navlat.ravel())
    ds['lon'] = np.unique(navlon.ravel())

    ds = ds.rename({'x': 'lon', 'y': 'lat','time_counter':'time',depthName:'depth'}).set_coords(['lat', 'lon'])
    ds = ds.drop('nav_lat')
    ds = ds.drop('nav_lon')

    try:
        ds = ds.drop('time_instant')
    except:
        pass
    try:
        ds = ds.drop('time_centered')
    except:
        pass

    ds['depth'].attrs['long_name'] = 'depth'
    ds['depth'].attrs['standard_name'] = 'depth'
    ds['lon'].attrs['standard_name'] = 'longitude'
    ds['lat'].attrs['standard_name'] = 'latitude'
    try:
        formatted_time = [datetime.strptime(str(t).split('.')[0], '%Y-%m-%d %H:%M:%S') for t in
                          ds.time.values]
    except:
        formatted_time = [datetime.strptime(str(t).split('.')[0], '%Y-%m-%dT%H:%M:%S') for t in
                          ds.time.values]
    ds['time'] = formatted_time
    return ds




def extractTimeseries(ds, var, depth_varName, mooring, year):
    dsMod=openNEMO(ds, depth_varName)

    ds=dsMod[var].sel(time=mooring.TIME.values, depth=2.5,method='nearest')

    # linear interpolation on observation location
    return ds.interp(lat= mooring.lat,lon=mooring.lon,method='linear').values

def getTgrid(conf,years):
    Tfile = glob(str(conf.dataset[conf.dataset[0]].path).format(exp=conf.dataset[conf.dataset[0]].exp, year=years[0], var='T'))
    ds=openNEMO(Tfile, 'deptht')
    return ds.lon.data,ds.lat.data

def BIAS(difference):
    return  np.nanmean(difference,axis=0)

def RMSE(difference):
    return np.sqrt(np.nanmean(difference**2,axis=0))

def ScatterIndex(data,obs):
    num=np.sum(((data-np.nanmean(data))-(obs-np.nanmean(obs)))**2)
    denom=np.sum(obs**2)
    return np.round(np.sqrt((num/denom)),3)

def saveDict(outname,dictionary_data):
    outfile = open(outname, "wb")
    pickle.dump(dictionary_data, outfile)
    outfile.close()


def main():
    exp=argv[1]
    year=argv[2]
    outfile=argv[3]
    conf = getConfigurationByID('conf.yaml', 'currents_rose')

    moorings = glob(conf.mooring.path)
    print('processing year %s ' % year)

    buffer=[]
    name_buffer=[]
    for moor in moorings:
        print (moor)
        mooring=xr.open_dataset(moor)
        mooring=mooring.isel(TIME=mooring.TIME.dt.year==int(year))
        mooring=mooring.isel(TIME=np.logical_not(np.isnan(mooring.DEPH)))

        _, index = np.unique(mooring['TIME'], return_index=True)
        mooring = mooring.isel(TIME=index)
        lat,lon=mooring.LATITUDE[0].values,mooring.LONGITUDE[0].values
        name_buffer.append(os.path.basename(moor).split('_')[0])
        mooring=mooring.drop('LATITUDE')
        mooring = mooring.drop('LONGITUDE')
        mooring['lat']=lat
        mooring['lon'] = lon
        print (mooring)
        dsMod_u = glob(str(conf.dataset.base).format(exp=exp, year=year, grid='U'))
        dsMod_v = glob(str(conf.dataset.base).format(exp=exp, year=year, grid='V'))

        mooring['mod_u']=(('TIME'),extractTimeseries(dsMod_u, conf.dataset.u, 'depthu', mooring, year))
        mooring['mod_v'] =(('TIME'),extractTimeseries(dsMod_v, conf.dataset.v, 'depthv', mooring, year))


        buffer.append(mooring)

    result=xr.concat(buffer,dim='station')
    result['station']=name_buffer

    result.to_netcdf(outfile)


if __name__=='__main__':
    main()


