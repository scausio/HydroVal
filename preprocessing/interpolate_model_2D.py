#!/usr/bin/env python
import intake
import xarray as xr
import numpy as np
import logging
from argparse import ArgumentParser


def interp(source, coords, **kwargs):
    """
    This is a more efficient version of DataArray.interp() for arrays that are
    not in memory. Where DataArray.interp() loads all the data, this loads only
    the coordinates and the nearest points.
    """
    index = {}
    kwargs['method'] = 'nearest'
    mask = np.zeros_like(len(coords['time']), dtype='bool')
    for dim, values in coords.items():

        tmp = xr.DataArray(np.arange(len(source[dim])), dims=dim)
        tmp.coords[dim] = source[dim]

        ind = tmp.interp({dim: values}, **kwargs)
        index[dim] = ind.fillna(0).astype(int)
        mask = np.logical_or(mask, np.isnan(ind))

    return source.isel(**index).where(~mask).load()


logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)
logger = logging.getLogger('model')

parser = ArgumentParser(description='Interpolate model results')
parser.add_argument('-c', '--catalog', default='catalog.yaml', help='catalog file')
parser.add_argument('-n', '--name', required=True, help='dataset name (in catalog)')
parser.add_argument('-s', '--start-date', help='start date')
parser.add_argument('-e', '--end-date', help='end date')
parser.add_argument('-i', '--input', required=True, help='input file')
parser.add_argument('-o', '--output', required=True, help='output file')

args = parser.parse_args()

logger.info('Opening input file %s' % args.input)
intermediate = xr.open_dataset(args.input)
intermediate['model'] = intermediate['model'].astype(str)  # Workaround for bug in xarray

logger.info('Opening catalog %s' % args.catalog)
cat = intake.open_catalog(args.catalog)

dataset = cat[args.name]
logger.info('Dataset "%s" contains %d files' % (args.name, len(dataset.files)))

if args.start_date:
    dataset = dataset.subset(date=slice(args.start_date, None))
if args.end_date:
    dataset = dataset.subset(date=slice(None, args.end_date))
logger.info('Using subset of %d files' % len(dataset.files))

model = dataset.read()

# Select nearest in all coordinates except depth
nearest_coords = {k: v.data for k, v in intermediate.coords.items() if k not in ['depth', 'model', 'dc_reference']}

#print(nearest_coords)

#model = interp(model.isel(depth=0), nearest_coords)  # FIXME: doesn't work (yet)
model = model.isel(depth=0).load()
model = model.chunk({'time': model['time'].size})
model = model.interp(nearest_coords, method='nearest').load()

print(model)

model = model.rename({'temperature': 'model_temperature'})
model.coords['model'] = xr.DataArray(np.array([args.name]), dims='model')
model = xr.concat([model], dim='model')

intermediate = intermediate.merge(model)

if args.output:
    logger.info('Writing output dataset to %s' % args.output)
    intermediate.to_netcdf(args.output)

