import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from utils import getConfigurationByID
import os
import seaborn as sns
import xarray as xr

sns.set_theme(style="whitegrid")


def main(exps,years,statistics=False,suptitle=False):
    print ('*** SALINITY VOLUME PLOTTING ***')
    conf=getConfigurationByID('conf.yaml', 'timeseries_salinityVolume')
    interm_base=getConfigurationByID('conf.yaml', 'hvFiles_dir')
    outdir_plots = os.path.join(conf.plot_conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')),
                                '-'.join(exps))
    os.makedirs(outdir_plots, exist_ok=True)

    plt.figure(figsize=(8, 5))
    ax = plt.gca()
    for exp in exps:
        buffer=[]
        for year in years:
            print (year)
            ds=xr.open_dataset(os.path.join(interm_base, f'{exp}_{year}_salVol.nc'))
            buffer.append(ds.isel(time=ds['time.year']==year))
        ds=xr.concat(buffer,dim='time')
        # if len(years)>1:
        #     intermFile = os.path.join(interm_base, f'{exp}_{years[0]}-{years[-1]}_salVol.npz')
        # else:
        #     intermFile = os.path.join(interm_base, f'{exp}_{years[0]}_salVol.npz')

        #ds = np.load(intermFile, allow_pickle=True)
        plt.plot(range(len(ds['time'])), ds['salinity'], label=exp)

    plt.legend()
    # plt.ylim(-15, 25)
    idx_ticks = np.arange(0, len(ds['time']), int(len(ds['time']) / 8))
    print (ds['time'])
    plt.xticks(idx_ticks, [str(t)[:16] for t in ds['time'].values[idx_ticks]], rotation=20,fontsize=9)
    plt.xlabel('Years')
    plt.ylabel('Salinity [$PSU$]')
    ax.grid(linestyle='-', linewidth=0.1, color='lightgray')
    plt.ylim(conf.plot_conf.ylims)
    # plt.show()
    # exit()
    plt.tight_layout()
    print (f'{exps} saved')
    plt.savefig(os.path.join(outdir_plots, f"{'-'.join(exps)}_SalVol_timeseries.png"))

    plt.clf()
