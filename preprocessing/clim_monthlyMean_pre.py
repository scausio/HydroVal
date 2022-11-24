#!/usr/bin/env python
import intake
import xarray as xr
import numpy as np
import logging
from argparse import ArgumentParser
import os
from nemo import u2t,v2t

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

logger = logging.getLogger('longrun')

parser = ArgumentParser(description='Process NEMO')
parser.add_argument('-c', '--catalog', default='catalog.yaml', help='catalog file')
parser.add_argument('-n', '--name', default='nemo4', help='dataset name (in catalog)')
parser.add_argument('-s', '--start-date', help='start date')
parser.add_argument('-e', '--end-date', help='end date')
parser.add_argument('-o', '--output', help='output file')

args = parser.parse_args()

logger.info('Opening catalog %s' % args.catalog)
cat = intake.open_catalog(args.catalog)

dataset = cat[args.name]
logger.info('Dataset "%s" contains %d files' % (args.name, len(dataset.files)))

if args.start_date:
    dataset = dataset.subset(date=slice(args.start_date, None))
if args.end_date:
    dataset = dataset.subset(date=slice(None, args.end_date))
logger.info('Using subset of %d files' % len(dataset.files))

ds = dataset.read()
base=os.path.dirname(args.output)
name=os.path.basename(args.output)

grid=name.split('_')[1]
if grid=='U':
    ds=u2t(ds,xdim='longitude')
elif grid=='V':
    ds = v2t(ds,ydim='latitude')
else:
    pass

lr_mean = ds.groupby("time.month").mean(dim='time')

#print(lr)

logger.info('Writing output dataset to %s' % args.output)
lr_mean.to_netcdf(os.path.join(base,f"{name}"))
lr_mean.mean(dim='month').to_netcdf(os.path.join(base,f"{name.replace('monthMean','yearlyMean')}"))