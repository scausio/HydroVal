import os
from glob import glob
import numpy as np
import xarray as xr
from natsort import natsorted
from utils import getConfigurationByID
from sys import argv

def timeseries(exp,conf,catalog, msk, years, npzname):

    time_ts = []
    sal_ts_vol = []
    Tmask = msk.tmask.values[0]
    volume = getBasinVolume(msk)
    #volume[volume==0]=np.nan
    volume[Tmask == 0] = np.nan
    volTot=np.copy(volume)
    volTot=np.nansum(volTot)
    outdir=os.path.dirname(npzname)
    expName=os.path.basename(npzname).split('_')[0]
    for year in years:
        print(f" computing {year}")
        fname = glob(catalog.args.urlpath.replace('{date:%Y%m%d}',f'{year}*').format('*'))
        print (catalog.args.urlpath.replace('{date:%Y%m%d}',f'{year}*').format('*'))
        ds = xr.open_mfdataset(fname, combine='by_coords')
        print (ds)
        sal_vol = getVolumeMean(ds, catalog.metadata.variables.salinity, Tmask, volume,volTot)
        #[sal_ts_vol.append(i) for i in sal_vol]
        #[time_ts.append(i) for i in ds.time_counter.values]
        #os.path.join(outdir, f'{expName}_{years[0]}_salVol.npz')
        np.savez(os.path.join(outdir, f'{expName}_{year}_salVol.npz'), sal_vol=sal_vol, time=ds.time_counter.values)
    print('concatenating npz')
    for year in years:
        ds=np.load(os.path.join(outdir, f'{expName}_{year}_salVol.npz'))
        [sal_ts_vol.append(i) for i in ds['sal_vol']]
        [time_ts.append(i) for i in ds['time']]
    np.savez(npzname, sal_vol=sal_ts_vol,time=time_ts)

def getVolumeMean(ds, variable, msk, vol,volTot):
    var = ds[variable].values
    print (var.shape, 'msk', msk.shape)
    var = var * vol
    #var.values[np.broadcast_to(msk, var.shape)] = np.nan
    print(var.shape, vol.shape)
    var = np.nansum(var,axis=(1,2,3))
    #vol[msk] = np.nan
    var = var / volTot
    print (var)
    return var

def getBasinVolume(msk):
    area = msk.e1t[0].values * msk.e2t[0].values
    volume = np.zeros_like(msk.e3t_0[0].values)
    for i, z in enumerate(msk.nav_lev):
        volume[i] = area * msk.e3t_0[0][i].values
    return volume

def parseYears(argsYears):
    yearsStr=argsYears.split(',')
    return[int(year) for year in yearsStr]

def main():
    exp=argv[1]
    years=parseYears(argv[2])
    outfile=argv[3]
    conf = getConfigurationByID('conf.yaml', 'timeseries_salinityVolume')
    catalog=getConfigurationByID('catalog_hydroval.yaml','sources')[ f'{exp}_T']

    mmsk = xr.open_dataset(getConfigurationByID('conf.yaml','mesh_mask'))
    print ('Preprocessing salinity Volume')
    timeseries(exp,conf,catalog, mmsk, years, outfile)
    print('done')

main()


