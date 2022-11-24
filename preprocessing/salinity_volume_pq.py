#!/usr/bin/env python
import intake
import xarray as xr
import numpy as np
import logging
from argparse import ArgumentParser
import os

def getVolumeMean(ds, variable, msk, vol,volTot):
    var = ds[variable].values
    print (var.shape, 'msk', msk.shape)
    var = var * vol
    print(var.shape, vol.shape)
    var = np.nansum(var,axis=(1,2,3))
    var = var / volTot
    print (var)
    return var

def getBasinVolume(msk):
    area = msk.e1t[0].values * msk.e2t[0].values
    volume = np.zeros_like(msk.e3t_0[0].values)
    for i, z in enumerate(msk.nav_lev):
        volume[i] = area * msk.e3t_0[0][i].values
    return volume



logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

logger = logging.getLogger('Salinity volume')

parser = ArgumentParser(description='Process NEMO')
parser.add_argument('-c', '--catalog', default='catalog.yaml', help='catalog file')
parser.add_argument('-n', '--name', default='nemo4', help='dataset name (in catalog)')
parser.add_argument('-m', '--meshmask', help='path to meshmask')
parser.add_argument('-s', '--start-date', help='start date')
parser.add_argument('-e', '--end-date', help='end date')
parser.add_argument('-o', '--output', help='output file')

args = parser.parse_args()

logger.info('Opening catalog %s' % args.catalog)
cat = intake.open_catalog(args.catalog)

dataset = cat[f"{args.name}_T"]
logger.info('Dataset "%s" contains %d files' % (args.name, len(dataset.files)))

if args.start_date:
    dataset = dataset.subset(date=slice(args.start_date, None))
if args.end_date:
    dataset = dataset.subset(date=slice(None, args.end_date))
logger.info('Using subset of %d files' % len(dataset.files))

ds = dataset.read()

mmsk = xr.open_dataset(args.meshmask)
Tmask = mmsk.tmask.values[0]

volume = getBasinVolume(mmsk)
volume[Tmask == 0] = np.nan
volTot = np.copy(volume)
volTot = np.nansum(volTot)

sal_vol = getVolumeMean(ds, 'salinity', Tmask, volume,volTot)
logger.info('Writing output dataset to %s' % args.output)
out_ds=ds['salinity'].copy().isel(latitude=0,longitude=0,depth=0)
out_ds=out_ds.drop(['time_centered','latitude','longitude','depth'])
out_ds.values=sal_vol
out_ds.to_netcdf(args.output)

