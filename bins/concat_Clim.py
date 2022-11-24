import xarray as xr
import os
import numpy as np
from glob import glob
from natsort import natsorted
from sys import argv

buffer=[]
fileList=natsorted(argv[1:])
outdir=os.path.dirname(argv[1])
years=[]

for f in fileList:
    fname_splitted=os.path.basename(f).split('_')
    if len(fname_splitted)>4:
        exp = '_'.join(fname_splitted[:-3])
        grid = fname_splitted[-3]
        year = fname_splitted[-2]
    else:
        exp = fname_splitted[0]
        grid = fname_splitted[1]
        year = fname_splitted[2]

    ds=xr.open_dataset(f)
    buffer.append(ds)
    years.append(year)

from_year=natsorted(list(set(years)))[0]
to_year=natsorted(list(set(years)))[-1]

outname=f'{exp}_{grid}_{from_year}-{to_year}_monthMean'
outDs=xr.concat(buffer,dim='month')
outDs.to_netcdf(os.path.join(outdir,f'{outname}.nc'))
