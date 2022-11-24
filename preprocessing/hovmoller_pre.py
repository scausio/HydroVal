import os
import xarray as xr
import numpy as np
from glob import glob
from utils import getConfigurationByID
from sys import argv


def yearlyExtraction(conf,catalog, exp, year, outfile):
    sal = catalog.metadata.variables.salinity
    temp =  catalog.metadata.variables.temperature
    level100m = conf.preproc.level100m

    # point_outname=os.path.join(outdir, '%s%02d_point.nc' %(year,month))
    # if os.path.exists(domain_outname) & os.path.exists(point_outname):
    if os.path.exists(outfile):
        print(f"{year} completed ")
    else:

        fs = glob(catalog.args.urlpath.replace('{date:%Y%m%d}',f'{year}*').format('*'))
        ds = xr.open_mfdataset(fs, combine='by_coords')
        ds = ds.where(ds[sal] != 0.)
        #ds.to_netcdf("test1.nc")
        ds = ds.where(ds['nav_lat'] >= conf.preproc.box.ymin)
        #ds = ds.where(ds['nav_lat'] < conf.preproc.box.ymax)
        #ds.to_netcdf("test2.nc")
        ds = ds.where(~xr.ufuncs.isnan(ds[sal].isel(deptht=level100m).drop('deptht')))

        del ds['time_centered']
        del ds['time_centered_bounds']
        del ds['time_counter_bounds']
        ds = ds.where(ds[sal] != 0.)
        # ds = ds.where(~xr.ufuncs.isnan(ds[sal].isel(deptht=level100m).drop('deptht'))) # 66 is the level of aproximaly 100 m depth. To remove the shallow areas
        # print (ds.nav_lat[:][0])
        ds_out = xr.Dataset({temp: (['time', 'depth', 'lat', 'lon'], ds[temp].values),
                             sal: (['time', 'depth', 'lat', 'lon'], ds[sal].values)},
                            coords={'depth': ds['deptht'].values, 'time': ds['time_counter'].values,
                                    'lat': np.sort(np.unique(ds.nav_lat.values.flatten()))[1:],
                                    'lon': np.sort(np.unique(ds.nav_lon.values.flatten()))[1:]})

        ds_out = ds_out.where(ds_out['lat'] > conf.preproc.box.ymin)

        dom = ds_out.mean(dim=['lat', 'lon'])
        dom.to_netcdf(outfile)
        del dom
        # if not os.path.exists(point_outname):
        #     pnt=ds_out.sel(lat=point[1], lon=point[0], method='nearest')
        #     pnt.to_netcdf(point_outname)
        #     print (pnt)
        #     del pnt

def main():
    exp=argv[1]
    year=argv[2]
    outfile=argv[3]
    conf = getConfigurationByID('conf.yaml', 'hovmoller')
    catalog= getConfigurationByID('catalog_hydroval.yaml', 'sources')[ f'{exp}_T']
    #  dataset:
    #base: '/work/opa/now_rsc/nemo/runs/{exp}/rebuilt/{exp}_1d_{year}*grid_T.nc'
    #os.makedirs(conf.outdir.format(hvPath=getConfigurationByID('conf.yaml', 'hvFiles_dir')),exist_ok=True)
    print('processing year %s ' % year)
    yearlyExtraction(conf,catalog, exp, year,outfile)
    print('done')

if __name__ == '__main__':
    main()








