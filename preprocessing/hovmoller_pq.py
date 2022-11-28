#!/usr/bin/env python
import intake
import xarray as xr
import numpy as np
import logging
from argparse import ArgumentParser
import os
from utils import getConfigurationByID



logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

logger = logging.getLogger('Hovmoller')

parser = ArgumentParser(description='Process NEMO')
parser.add_argument('-c', '--catalog', default='catalog.yaml', help='catalog file')
parser.add_argument('-n', '--name', default='nemo4', help='dataset name (in catalog)')
parser.add_argument('-s', '--start-date', help='start date')
parser.add_argument('-e', '--end-date', help='end date')
parser.add_argument('-o', '--output', help='output file')

args = parser.parse_args()

logger.info('Opening catalog %s' % args.catalog)
cat = intake.open_catalog(args.catalog)

dataset = cat[f"{args.name}_T"]
logger.info('Dataset "%s" contains %d files' % (args.name, len(dataset.files)))
conf = getConfigurationByID(os.path.join(os.path.dirname(args.catalog),'conf.yaml'), 'hovmoller')

if args.start_date:
    dataset = dataset.subset(date=slice(args.start_date, None))
if args.end_date:
    dataset = dataset.subset(date=slice(None, args.end_date))
logger.info('Using subset of %d files' % len(dataset.files))

ds = dataset.read()
print (ds)
mindepth = conf.preproc.minDepth

if os.path.exists(args.output):
    print(f"{year} completed ")
else:
    ds = ds.where(ds['salinity'] != 0.)
    ds = ds.where((ds['latitude'] >= conf.preproc.box.ymin) & (ds['latitude'] < conf.preproc.box.ymax) &
                  (ds['longitude'] >= conf.preproc.box.xmin) & (ds['longitude'] < conf.preproc.box.xmax))
    ds = ds.where(~xr.ufuncs.isnan(ds['salinity'].sel(depth=mindepth, method='nearest')))
    print(ds.time)

    out_ds = ds.mean(dim=['latitude', 'longitude'])
    logger.info('Writing output dataset to %s' % args.output)
    out_ds.to_netcdf(args.output)



