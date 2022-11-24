
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import os
from mpl_toolkits.basemap import Basemap
from datetime import date, timedelta
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cmocean import cm
from .utils import getConfigurationByID
import seaborn as sns
sns.set_theme(style="whitegrid")

clrs = ['r', 'b', 'g', 'y','m']
def getTicks(years):
    days = dayList(years, noleap=True)
    day_ticks = []
    for year in years:
        for i in range(1, 13):
            day = '%s%02d01' % (year, i)
            n = days.index(day)
            day_ticks.append([day, n])
            if year==years[-1]:
                if i==12:
                    day = '%s1231' % (year)
                    n = days.index(day)
                    day_ticks.append([day, n])

    return day_ticks

def manageTicks(years, day_ticks):
    if (len(years) < 2):
        day_ticks_short = day_ticks
    elif (len(years) > 2) and (len(years) < 5):
        day_ticks_short = day_ticks[:, ::3]

    elif (len(years) > 5) and (len(years) < 10):
        day_ticks_short = day_ticks[:, ::6]
    else:
        day_ticks_short = day_ticks[:, ::12]
    return day_ticks_short

def noLeap(days):
    out=[]
    for day in days:
        if day[4:]=='0229':
            pass
        else:
            out.append(day)
    return out

def dayList(years, noleap=False):
    sdate = date(years[0], 1, 1)   # start date
    edate = date(years[-1], 12, 31)   # end date
    delta = edate - sdate       # as timedelta
    days=[(sdate + timedelta(days=d)).strftime('%Y%m%d') for d in range(delta.days+1)]
    if noleap:
        return noLeap(days)
    else:
        return days

def setDicts(datasets):
    yearly_1Dbias = {}
    yearly_1Drmse = {}
    yearly_2Dbias = {}
    yearly_2Drmse = {}
    for ds in datasets:
        yearly_1Dbias[ds]=[]
        yearly_1Drmse[ds]=[]
        yearly_2Dbias[ds]=[]
        yearly_2Drmse[ds]=[]
    return yearly_1Dbias,yearly_1Drmse,yearly_2Dbias,yearly_2Drmse

def concatYears(statistics_dict, exp_names):
    concatenated={}
    for ds in exp_names:
        concatenated[ds] = xr.concat(statistics_dict[ds], 'time')
    return concatenated



def main(exps,years):
    plt.rcParams["figure.figsize"] = 5, 8

    plt.rcParams.update({'font.size': 14,"font.serif":"Palatino"})

    print('*** SST PLOTTING ***')
    conf = getConfigurationByID('conf.yaml','sst')

    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')), '-'.join(exps))
    os.makedirs(outdir_plots,exist_ok=True)
    interm_path=getConfigurationByID('conf.yaml','hvFiles_dir')

    try:
        lsm=np.load(conf.lsm)
    except:
        lsm=False

    box=conf.postproc.domain.box
    meridians = np.arange(box.xmin, box.xmax, 2)
    parallels = np.arange(box.ymin, box.ymax, 2)

    yearly_1Dbias,yearly_1Drmse,yearly_2Dbias,yearly_2Drmse=setDicts(exps)

    day_ticks=getTicks(years)

    for year in years:

        filesToPlot=[os.path.join(interm_path,f'{exp_name}_T_{year}_sst.nc'.format(exp_name=exp_name,year=year)) for exp_name in exps]
        nc_all = xr.open_mfdataset(filesToPlot, combine='by_coords').compute()
        print (filesToPlot)

        for i,exp in enumerate(nc_all.model):
            # convert exp_name
            exp_name=exps[i]
            nc=nc_all.sel(model=exp)
            model_temp=nc['model_temperature'].values

            if lsm:
                model_temp[~lsm]=np.nan
            model_temp=model_temp.transpose(2,0,1)

            mod_obs_difference= model_temp - nc['temperature']

            # DISCARD DIFFERENCE GREATER THAN threshold degC
            mod_obs_difference.values[np.abs(mod_obs_difference.values)>float(conf.postproc.threshold.bias)]=np.nan
            print (mod_obs_difference)
            bias_2D=mod_obs_difference.mean(dim='time',skipna=True)
            print (bias_2D)
            rmse_2D=np.sqrt((bias_2D**2))

            bias_1D=np.nanmean(mod_obs_difference, axis=(1, 2))
            rmse_1D=np.sqrt(np.nanmean(mod_obs_difference**2,axis=(1,2)))

            [yearly_1Dbias[exp_name].append(i)for i in bias_1D]
            [yearly_1Drmse[exp_name].append(i) for i in rmse_1D]
            yearly_2Dbias[exp_name].append(bias_2D)
            yearly_2Drmse[exp_name].append(rmse_2D)

    day_ticks=np.array(day_ticks).astype(int).T

    concat_bias=concatYears(yearly_2Dbias,exps)
    concat_rmse=concatYears(yearly_2Drmse,exps)
    text_bias=[]
    text_rmse=[]

    # PLOT TIMESERIES
    fig_ts, (ax3, ax4) = plt.subplots(nrows=2, sharex=True)
    fig_ts.set_size_inches(6, 4.5)
    if len(years)>1:
        ax3.set_title(f'SST_{conf.dataset_type} [{years[0]}-{years[-1]}]')

    else:
        ax3.set_title(f'SST_{conf.dataset_type} [{years[0]}]')

    ax3.set_ylabel('Bias [degC]')
    ax4.set_ylabel('RMSE')

    rmse_alldiff=[]

    for i,ds in enumerate(exps):
        bias=concat_bias[ds].mean('time',skipna=True)
        rmse = concat_rmse[ds].mean('time',skipna=True)

        # PLOT MAPS
        fig = plt.figure()
        fig.set_size_inches(6, 4.5)
        if len(years)>1:
            fig.suptitle(f'SST_{conf.dataset_type} {ds} [{years[0]}-{years[-1]}]')
        else:
            fig.suptitle(f'SST_{conf.dataset_type} {ds} [{years[0]}]')
        ax1 = fig.add_subplot(211)
        m = Basemap(llcrnrlon=box.xmin, llcrnrlat=box.ymin, urcrnrlat=box.ymax, urcrnrlon=box.xmax, resolution='l')
        m.drawcoastlines()
        m.fillcontinents('Whitesmoke')
        m.drawparallels(parallels, labels=[True, False, False, True], linewidth=0.1)
        m.drawmeridians(meridians, labels=[False, False, False, False], linewidth=0.1)

        im_bias = ax1.imshow(bias, origin='bottom', cmap=cm.balance, vmin=conf.postproc.bias.min,
                             vmax=conf.postproc.bias.max,
                             extent=[nc.longitude.min(), nc.longitude.max(), nc.latitude.min(), nc.latitude.max()])
        plt.colorbar(im_bias)
        plt.title('Bias [degC]', loc='left')

        ax2 = fig.add_subplot(212)

        m = Basemap(llcrnrlon=box.xmin, llcrnrlat=box.ymin, urcrnrlat=box.ymax, urcrnrlon=box.xmax, resolution='l')
        m.drawcoastlines()
        m.fillcontinents('Whitesmoke')
        m.drawparallels(parallels, labels=[True, False, False, True], linewidth=0.1)
        m.drawmeridians(meridians, labels=[True, True, False, True], linewidth=0.1)
        rmse_alldiff.append(rmse)
        im_rmse = ax2.imshow(rmse, origin='bottom', cmap=cm.thermal, vmin=conf.postproc.rmse.min, vmax=conf.postproc.rmse.max,
                             extent=[nc.longitude.min(), nc.longitude.max(), nc.latitude.min(), nc.latitude.max()])

        plt.colorbar(im_rmse)
        plt.title('RMSE [degC]', loc='left')
        #plt.show()
        fig.savefig((os.path.join(outdir_plots, f'{years[0]}-{years[-1]}mean_{ds}_maps.png')))
        plt.close(fig)

        day_ticks_short=manageTicks(years, day_ticks)

        monthly_bias = []
        monthly_rmse = []

        for ii,jj in zip(day_ticks[1][:-1],day_ticks[1][1:]):
            print (yearly_1Dbias[ds][ii:jj])
            monthly_bias.append(np.nanmean(yearly_1Dbias[ds][ii:jj]))
            monthly_rmse.append(np.nanmean(yearly_1Drmse[ds][ii:jj]))
            n = ii

        ax3.plot([0, len(yearly_1Dbias[ds])], [0, 0], c='k', linewidth=1, linestyle='dotted')
        ax3.plot(yearly_1Dbias[ds], label='%s DM' % ds, c=clrs[i], alpha=0.5,linewidth=1)
        ax3.plot(day_ticks[1][:-1], monthly_bias, label='%s MM' % ds)#, linestyle='dashed', linewidth=3)
        #
        ax4.plot(yearly_1Drmse[ds], label='%s DM' % ds, c=clrs[i],alpha=0.5, linewidth=1)
        ax4.plot(day_ticks[1][:-1], monthly_rmse, label='%s' % ds )#, linestyle='dashed', linewidth=3)

        #from scipy import  signal
        #ax3.plot(day_ticks[1][:-1], signal.detrend(monthly_bias)+np.nanmean(monthly_bias), label='%s MM ' % ds, c='g')

        text_bias.append('bias %s= %s ' % (ds, np.round(np.nanmean(yearly_1Dbias[ds]), 2)))
        text_rmse.append('RMSE %s= %s ' % (ds, np.round(np.nanmean(yearly_1Drmse[ds]), 3)))
        # print('cumulative bias=%s %s ' % (np.nanmean(yearly_1Dbias[ds]), ds))
        # print('cumulative rmse=%s %s ' % (np.nanmean(yearly_1Drmse[ds]), ds))

    ax3.annotate('\n'.join(text_bias), xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9)
    ax4.annotate('\n'.join(text_rmse), xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9)
    ax3.legend(loc='lower right', fontsize=8)

    ax4.set_xticks(day_ticks_short[1])
    ax4.set_xticklabels(day_ticks_short[0], rotation=90,fontsize=8)
    fig_ts.tight_layout()
    fig_ts.savefig((os.path.join(outdir_plots, f'{years[0]}-{years[-1]}_ts.png')))
    plt.close()

    if len(exps)==2:
        fig,ax=plt.subplots()
        fig.set_size_inches(6, 4.5)
        m = Basemap(llcrnrlon=box.xmin, llcrnrlat=box.ymin, urcrnrlat=box.ymax, urcrnrlon=box.xmax, resolution='l')
        m.drawcoastlines()
        m.fillcontinents('Whitesmoke')
        m.drawparallels(parallels, labels=[True, False, False, True], linewidth=0.1)
        m.drawmeridians(meridians, labels=[True, True, False, True], linewidth=0.1)

        im_rmse = ax.imshow(rmse_alldiff[1]-rmse_alldiff[0], origin='bottom', cmap=cm.balance, vmin=-0.5, vmax=0.5,
                             extent=[rmse.longitude.min(), rmse.longitude.max(), rmse.latitude.min(), rmse.latitude.max()])

        plt.title(f'RMSE difference {exps[1]}-{exps[0]}')

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im_rmse,cax=cax)
        #plt.show()
        fig.savefig((os.path.join(outdir_plots, f'{years[0]}-{years[-1]}mean_{ds}_maps_diff.png')))
        plt.close(fig)

        """
        •	Region 1: NW shelf: 27-34E 43-47N 
        •	Region 2: SW and Bosporus area: 27-32E 41-43N "
        •	Region 3: Crimea and Kerch: 32-38E 43.5-46N 
        •	Region 4: SE part - Batumi area: 38-42E 40.5-45N 
        •	Region 5: South coast – Sinop area: 31-38E 40.5-43N
        """
        area=xr.Dataset()
        area['lat']=('lat',rmse.latitude)
        area['lon']=('lon',rmse.longitude)
        area['diff']=(('lat','lon'),rmse_alldiff[1]-rmse_alldiff[0])
        area['rel_diff']=(('lat','lon'),((rmse_alldiff[1]-rmse_alldiff[0])/rmse_alldiff[0])*100)
        #area.to_netcdf('/Users/scausio/Documents/data/PHD/hydro_validation/SST_perNEWArea.nc')
        print (area)
        bbox={}
        bbox['NW']=[[27,33],[44.4,47]]
        bbox['S']=[[27,33],[40.5,44.4]]
        bbox['C']=[[33,37],[40.5,46]]
        bbox['E']=[[37,42],[40.5,45]]

        for a,box in bbox.items():
            print (a,box)
            #print (a,area['diff'].sel(lat=(area.lat>box[1][0])&(area.lat<box[1][1]),lon=(area.lon>box[0][0])&(area.lon<box[0][1])).mean(skipna=True))
            print(a, area['diff'].sel(lat=slice( box[1][0], box[1][1]),
                                      lon=slice(box[0][0],box[0][1])).mean(skipna=True),
                  area['rel_diff'].sel(lat=slice( box[1][0], box[1][1]),
                                      lon=slice(box[0][0],box[0][1])).mean(skipna=True))
