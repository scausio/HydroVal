import xarray as xr
import matplotlib.pyplot as plt
from glob import glob
import os


base='/work/opa/da01720/Experiments/CMEMS2_n4.2/bs-test-int-bdy7/rebuilt/40_1d_{year}*_*_grid_{grid}.nc'

years=range(2016,2020)
grids=['T','U','V']
idxs={}
idxs['T']=[[80,range(9,17)],[45,range(79,8,-1)],[45,range(10,23)]]
idxs['U']=[[79,range(9,17)],[45,range(78,8,-1)],[45,range(10,23)]]
idxs['V']=[[80,range(9,16)],[45,range(79,8,-1)],[45,range(10,22)]]

for year in years:
    base_y
