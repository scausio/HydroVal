import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bins.utils import getConfigurationByID,safeOpenMFdataset
import os
import seaborn as sns
import xarray as xr

sns.set_theme(style="whitegrid")


umeas={}
umeas['temperature']='Temperature [$°C$]'
umeas['salinity']='Salinity [$PSU$]'
umeas['ssh']='Sea Surface Height [$m$]'


def plot(conf,exps,var,years,interm_base,outdir_plots,suptitle,statistics, depth,i,anomaly=False):
    plt.figure(figsize=(7, 6))
    ax = plt.gca()
    text_stats = [ r"$\bf{Avg:}$" + " " ]
    custom_palette = sns.color_palette("Paired", 10)
    print (custom_palette[4])
    ni=0
    for n,exp in enumerate(exps):
        n+=ni
        intermFiles = []
        for year in years:
            intermFiles.append(os.path.join(interm_base, f'{exp}_{conf.variables[var].grid}_{year}_domainAverage.nc'))

        if var == 'ssh':
            ds = safeOpenMFdataset(intermFiles)
        else:
            ds =safeOpenMFdataset(intermFiles).sel(depth=depth, method='nearest')


        ds=ds.sel(time=ds.time.dt.year.isin(years))

        if anomaly:

            ym=ds[var].groupby('time.year').mean('time',skipna=True)-np.nanmean(ds[var])
            monthMean=ds[var].groupby('time.month').mean('time',skipna=True).compute()
            mm = ds[var].resample(time="1M").mean(skipna=True).compute()
            for i,month in enumerate(mm):
                month_id=int((str(month.time.values)).split('-')[1])
                mm.values[i]-=monthMean.sel(month=month_id)

            monthsLen=len(mm)

            firstMonth=int((str(mm[0].time.values)).split('-')[1])
            allTicks=np.array([(str(m)[:7]).replace('-','') for m in mm.time.values])
            print(np.arange(firstMonth, monthsLen, 12))
            print(n)
            ax.plot(np.arange(firstMonth-1,monthsLen,12), ym,label=f'YM {exp}',linewidth=3,color=custom_palette[n])
            ax.plot(range(monthsLen),mm,marker='x', linewidth=1,label=f'MM {exp}',color=custom_palette[n+1])
            ni+=1

            #print(mm)
            idx_ticks = np.arange(0, monthsLen, int(monthsLen/ len(years)))
            print (idx_ticks)

            plt.xticks(idx_ticks,allTicks[idx_ticks], rotation=40, fontsize=9)

        else:
            plt.plot(range(len(ds['time'])), ds[var], label=exp)
            idx_ticks = np.arange(0, len(ds['time']), int(len(ds['time']) / 8))
            plt.xticks(idx_ticks, [str(t)[:16] for t in ds['time'].values[idx_ticks]], rotation=40, fontsize=9)
        text_stats.append('%s: %s' % (exp, np.round(np.nanmean( ds[var]), 2)))


    # plt.ylim(-15, 25)


    plt.xlabel('Years')
    plt.ylabel(umeas[var])

    ax.grid(linestyle=':', linewidth=0.1, color='lightgray')
    # plt.show()
    # exit()
    if suptitle:
        if anomaly:
            plt.title(f'Anomaly of Domain averaged {var} {years[0]}-{years[-1]}')
        else:
            plt.title(f'Domain averaged {var} {years[0]}-{years[-1]}')


    if var == 'ssh':
        if anomaly:
            outname = os.path.join(outdir_plots, f"anom_{'-'.join(exps)}_{var}_timeseries.png")
        else:
            outname = os.path.join(outdir_plots, f"{'-'.join(exps)}_{var}_timeseries.png")
        try:
            if type(conf.variables[var].ylims):
                plt.ylim(conf.variables[var].ylims)
        except:
            pass
    else:
        if anomaly:
            outname = os.path.join(outdir_plots, f"anom_{'-'.join(exps)}_{var}_{depth}-depth_timeseries.png")
        else:
            outname = os.path.join(outdir_plots, f"{'-'.join(exps)}_{var}_{depth}-depth_timeseries.png")
        try:
            if conf.variables[var].ylims[i]:
                plt.ylim(conf.variables[var].ylims[i])
        except:
            pass
    if statistics:
        plt.annotate('\n'.join(text_stats), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=10)
    plt.legend(loc='best')
    plt.tight_layout()

    plt.savefig(outname)
    plt.close()




def main(exps,years,statistics=False,suptitle=False):
    print ('*** TIMESERIES PLOTTING ***')
    conf=getConfigurationByID('conf.yaml', 'timeseries_domainAvg').plot_conf
    interm_base=getConfigurationByID('conf.yaml', 'hvFiles_dir')
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')),
                                '-'.join(exps))
    os.makedirs(outdir_plots, exist_ok=True)
    for var in conf.variables:
        if var =='ssh':
            plot(conf, exps, var, years, interm_base, outdir_plots, suptitle,statistics, 0, 0)
        else:
            for i,depth in enumerate(conf.variables[var].depth):
                plot(conf, exps, var, years, interm_base, outdir_plots, suptitle,statistics,depth,i)


