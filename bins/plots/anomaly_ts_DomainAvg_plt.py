import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from utils import getConfigurationByID
import os
import seaborn as sns
import xarray as xr
from .ts_DomainAvg_plt import umeas,plot
sns.set_theme(style="whitegrid")


def main(exps,years,statistics=False,suptitle=False):
    print ('*** ANMOALIES TIMESERIES PLOTTING ***')
    conf=getConfigurationByID('conf.yaml', 'anomaly_timeseries_domainAvg').plot_conf
    interm_base=getConfigurationByID('conf.yaml', 'hvFiles_dir')
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')),
                                '-'.join(exps))
    os.makedirs(outdir_plots, exist_ok=True)
    for var in conf.variables:
        if var =='ssh':
            plot(conf, exps, var, years, interm_base, outdir_plots, suptitle,statistics, 0, 0,anomaly=True)
        else:
            for i,depth in enumerate(conf.variables[var].depth):
                plot(conf, exps, var, years, interm_base, outdir_plots, suptitle,statistics,depth,i,anomaly=True)


