import matplotlib
matplotlib.use('Agg')
import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from cmocean import cm
from utils import getConfigurationByID,computeAnomaly
from .hovmoller_plt import hovmoller


def main(runningDir,exps,years):
    print('*** ANOMALIES HOVMOLLER PLOTTING ***')
    interm_base=getConfigurationByID(os.path.join(runningDir,'conf.yaml'),'hvFiles_dir')
    datatypes=['domain']#'point',
    conf = getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'anomaly_hovmoller')
    for datatype in datatypes:
        print (datatype)
        for exp in exps:
            hovmoller(runningDir,interm_base,years,exp, datatype,conf,anomaly=True)



