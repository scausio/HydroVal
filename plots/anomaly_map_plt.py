import matplotlib
import xarray as xr
matplotlib.use('Agg')
from bins.utils import getConfigurationByID,safeOpenMFdataset,umeas
import os
import seaborn as sns
from .ts_DomainAvg_plt import plot
from .plotting_tools import plotMap

sns.set_theme(style="whitegrid")


def main(exps,years):
    print ('*** ANOMALY MAPS PLOTTING ***')
    conf=getConfigurationByID('conf.yaml', 'anomaly_maps').plot_conf
    interm_base=getConfigurationByID('conf.yaml', 'hvFiles_dir')
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')),
                                '-'.join(exps))
    os.makedirs(outdir_plots, exist_ok=True)

    for exp in exps:
        print (exp)
        for var in conf.variables:
            print (var)
            variable_config =conf.variables[var]
            try:
                time_mean = xr.open_dataset(os.path.join(interm_base, f'{exp}_{variable_config.grid}_{years[0]}-{years[-1]}_mean.nc'))
            except:
                exit('file not available, please run Climatologies.total')

            for year in years:
                print (year)
                ds = xr.open_dataset(os.path.join(interm_base, f'{exp}_{variable_config.grid}_{year}_yearlyMean.nc'))[var]

                if var == 'ssh':
                    title = f'{year} SSH anomaly'
                    anom=ds - time_mean[var]

                else:
                    depth = int(variable_config.depth)
                    ds = ds.sel(depth=depth, method='nearest')
                    title = f'{year} {var.capitalize()} anomaly - depth {depth}m '
                    if depth == 0:
                        if var == 'temperature':
                            title = f'{year} SST anomaly'
                    anom = ds - time_mean[var].sel(depth=depth, method='nearest')
                outname=os.path.join(outdir_plots,f'mapAnom_{var}_{year}_{depth}m')

                plotMap(anom, variable_config.cmap, variable_config.vmin, variable_config.vmax, outname, resolution=conf.coast_resolution, title=title,cbar_title=umeas[var]['mean'])


