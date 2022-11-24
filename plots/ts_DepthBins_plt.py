import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bins.utils import getConfigurationByID
import os
import seaborn as sns
import xarray as xr

sns.set_theme(style="whitegrid")

umeas={}
umeas['temperature']='Temperature [$°C$]'
umeas['salinity']='Salinity [$PSU$]'

def main(exps,years,statistics=False,suptitle=False):
    print ('*** TIMESERIES PLOTTING ***')
    conf=getConfigurationByID('conf.yaml', 'timeseries_depthBins').plot_conf
    interm_base=getConfigurationByID('conf.yaml', 'hvFiles_dir')
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')),
                                '-'.join(exps))
    os.makedirs(outdir_plots, exist_ok=True)
    for var in conf.variables:

        bins_=list(zip(conf.variables[var].bins[:-1],conf.variables[var].bins[1:]))
        for i,bin_ in enumerate(bins_):
            text_stats = [r"$\bf{Avg:}$" + " "]
            plt.figure(figsize=(8, 6))
            ax = plt.gca()

            for exp in exps:

                intermFiles = []
                for year in years:
                    intermFiles.append(os.path.join(interm_base, f'{exp}_{conf.variables[var].grid}_{year}_domainAverage.nc'))

                    ds = xr.open_mfdataset(intermFiles, data_vars='minimal').sel(depth=slice(bin_[0],bin_[1])).mean(dim='depth',skipna=True)
                plt.plot(range(len(ds['time'])), ds[var], label=exp)
                text_stats.append('%s: %s' % (exp, np.round(np.nanmean(ds[var]), 2)))

            # plt.ylim(-15, 25)
            idx_ticks = np.arange(0, len(ds['time']), int(len(ds['time']) / 8))
            plt.xticks(idx_ticks, [str(t)[:16] for t in ds['time'].values[idx_ticks]], rotation=20,fontsize=9)
            plt.xlabel('Years')
            plt.ylabel(umeas[var])

            ax.grid(linestyle=':', linewidth=0.1, color='lightgray')
            # plt.show()
            # exit()
            if suptitle:
                plt.title(f'Domain averaged {var} depth:{bin_[0]}-{bin_[1]}m [{years[0]}-{years[-1]}]')

            if statistics:
                plt.annotate('\n'.join(text_stats), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=10)
            if type(conf.variables[var].ylims[i]):
                plt.ylim(conf.variables[var].ylims[i])

            outname=os.path.join(outdir_plots, f"{'-'.join(exps)}_{var}_{bin_[0]}-{bin_[1]}m_timeseries.png")
            plt.legend(loc='best')
            plt.savefig(outname)
            plt.close()
