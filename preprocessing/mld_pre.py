import os
import xarray as xr
import numpy as np
from glob import glob
from utils import getConfigurationByID,getEmptyMonthlyResult
from sys import argv
import pandas as pd
import seawater as sw

def get_MLD_1D_temp(ds, tempName,depths,delta_temp=0.2,min_depth=10):
    pass

def get_MLD_1D_dens(ds,tempName,salName,depths,delta_dens=0.01,min_depth=10):
    #dens=sw.dens(ds[salName],ds[tempName],depths)
    dens = sw.dens0(ds[salName], ds[tempName])
    print (dens.shape)
    d10 = dens[np.searchsorted(depths,min_depth)]
    if np.isnan(d10):
        return np.nan
    else:
        MLD = depths[np.searchsorted(dens,d10+delta_dens)]
        return max(MLD,min_depth)

def month_meterAveraged(ds,year,conf):
    model_name=ds.model.values

    monthly_ds = ds.isel(model=0).groupby('time.month')
    print(monthly_ds)

    buffer_time = []
    buffer_obs = []
    buffer_mod = []
    profiles=[]

    for group in monthly_ds:
        lowlim=int(np.nanmin(group[1].depth.values))
        uplim= int(np.nanmax(group[1].depth.values)) if int(np.nanmax(group[1].depth.values))<180 else 180
        depths = np.arange(lowlim - .5,uplim+.5, 1)

        month_val = group[1].groupby_bins('depth',bins=depths).mean()

        month_val = month_val.rename(depth_bins='depth')
        #o['month']=pd.to_datetime(f"{year}-{group[0]}")
        depth=(pd.IntervalIndex(month_val['depth'].values).mid)
        #o['depth'].values = depth
        #result['obs_mld']=get_MLD_1D_temp(o, 'temperature', depth, delta_temp=0.2, min_depth=10)

        try:
            obs=get_MLD_1D_dens(month_val, 'temperature', 'salinity',depth, delta_dens=conf.delta_dens, min_depth=conf.min_depth)
            mod=get_MLD_1D_dens(month_val, 'model_temperature', 'model_salinity', depth, delta_dens=conf.delta_dens, min_depth=conf.min_depth)
            profiles.append(len(np.unique(group[1].time.values)))
        except:
            obs=np.nan
            mod=np.nan
            profiles.append(0)

        buffer_obs.append(obs)
        buffer_mod.append(mod)
        buffer_time.append(pd.to_datetime(f"{year}-{group[0]}"))

    result=xr.Dataset()
    result['model'] = (('model'), model_name)
    result['month']=(('month'),buffer_time)
    result['obs_mld']=(('model','month'),[ buffer_obs])
    result['mod_mld'] = (('model','month'), [buffer_mod])
    result['profiles'] = (('model', 'month'), [profiles])

    if len(result.month)==12:
        return result
    else:
        result_=getEmptyMonthlyResult(model_name,year)
        for i,month in enumerate(range(1,13)):
            try:
                result_['obs_mld'].values[0,i] = result.sel(month=result.month.dt.month==month)['obs_mld'].values
                result_['mod_mld'].values[0,i] =result.sel(month=result.month.dt.month==month)['mod_mld'].values
                result_['profiles'].values[0,i]= result.sel(month=result.month.dt.month==month)['profiles'].values
            except:
                pass
        return result_

##### cerca di capire come calcolare bias e rmse del mld. Questo lo farai nella fx seguente, che per ora si chiama daily_meterAveraged, che é una copia della monthmeterAverage
def daily_meterAveraged(ds, year, conf):
    model_name = ds.model.values

    ds['diff_T'] = ds['model_temperature'] - ds['temperature']
    ds['diff_S'] = ds['model_salinity'] - ds['salinity']
    print(0)
    print(ds)
    print(1)
    monthly_ds = ds.isel(model=0).groupby('time.month')
    print(monthly_ds)
    print(2)
    buffer_time = []
    buffer_obs = []
    buffer_mod = []
    profiles = []

    for group in monthly_ds:

        lowlim = int(np.nanmin(group[1].depth.values))
        uplim = int(np.nanmax(group[1].depth.values)) if int(np.nanmax(group[1].depth.values)) < 180 else 180
        depths = np.arange(lowlim - .5, uplim + .5, 1)

        month_val = group[1].groupby_bins('depth', bins=depths).mean()

        month_val = month_val.rename(depth_bins='depth')
        # o['month']=pd.to_datetime(f"{year}-{group[0]}")
        depth = (pd.IntervalIndex(month_val['depth'].values).mid)
        # o['depth'].values = depth
        # result['obs_mld']=get_MLD_1D_temp(o, 'temperature', depth, delta_temp=0.2, min_depth=10)

        try:
            obs = get_MLD_1D_dens(month_val, 'temperature', 'salinity', depth, delta_dens=conf.delta_dens,
                                  min_depth=conf.min_depth)
            mod = get_MLD_1D_dens(month_val, 'model_temperature', 'model_salinity', depth, delta_dens=conf.delta_dens,
                                  min_depth=conf.min_depth)
            profiles.append(len(np.unique(group[1].time.values)))
        except:
            obs = np.nan
            mod = np.nan
            profiles.append(0)

        buffer_obs.append(obs)
        buffer_mod.append(mod)
        buffer_time.append(pd.to_datetime(f"{year}-{group[0]}"))

    result = xr.Dataset()
    result['model'] = (('model'), model_name)
    result['month'] = (('month'), buffer_time)
    result['obs_mld'] = (('model', 'month'), [buffer_obs])
    result['mod_mld'] = (('model', 'month'), [buffer_mod])
    result['profiles'] = (('model', 'month'), [profiles])

    if len(result.month) == 12:
        return result
    else:
        result_ = getEmptyMonthlyResult(model_name, year)
        for i, month in enumerate(range(1, 13)):
            try:
                result_['obs_mld'].values[0, i] = result.sel(month=result.month.dt.month == month)['obs_mld'].values
                result_['mod_mld'].values[0, i] = result.sel(month=result.month.dt.month == month)['mod_mld'].values
                result_['profiles'].values[0, i] = result.sel(month=result.month.dt.month == month)['profiles'].values
            except:
                pass
        return result_



def mld_1D(exp,year,conf,outfile):

    print ('*** MLD timeseries PREPROCESSING ***')
    interm_tmpl = os.path.join(getConfigurationByID('conf.yaml', 'hvFiles_dir'), '{exp}_{year}_argo.nc')
    try:
        ds_year = xr.open_dataset(interm_tmpl.format(year=year, exp=f'{exp}_T'))
        mmean_ds=month_meterAveraged(ds_year, year,conf)
        daily_meterAveraged(ds_year, year,conf)
        mmean_ds.to_netcdf(outfile)
    except:

        ds=getEmptyMonthlyResult([f'{exp}_T'],year)
        ds.to_netcdf(outfile)

def mld_2D(exp,year,conf,outfile):
    pass

def main():
    exp=argv[1]
    year=argv[2]
    outfile=argv[3]
    conf = getConfigurationByID('conf.yaml', 'mld')
    mld_1D(exp,year,conf,outfile)
    mld_2D(exp, year, conf, outfile)

if __name__ == '__main__':
    main()







