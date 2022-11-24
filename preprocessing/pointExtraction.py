#!/usr/bin/env python
import intake
import xarray as xr
import numpy as np
import logging
from argparse import ArgumentParser
import os

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

logger = logging.getLogger('longrun')

parser = ArgumentParser(description='Process NEMO')
parser.add_argument('-c', '--catalog', default='catalog.yaml', help='catalog file')
parser.add_argument('-n', '--name', default='nemo4', help='dataset name (in catalog)')
parser.add_argument('-s', '--start-date', help='start date')
parser.add_argument('-e', '--end-date', help='end date')
parser.add_argument('-o', '--output', help='output file')
parser.add_argument('-lon', '--longitude', help='longitude')
parser.add_argument('-lat', '--latitude', help='latitude')

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
lr_slice = ds.sel(longitude=args.lon,latitude=args.lat, method='nearest')


#print(lr)

if args.output:
    base=os.path.dirname(args.output)
    name= f"lon{args.lon}_lat{args.lat}_{os.path.basename(args.output)}"
    logger.info('Writing output dataset to %s' % args.output)
    lr_slice.to_netcdf(os.path.join(base,f"{name}"))
