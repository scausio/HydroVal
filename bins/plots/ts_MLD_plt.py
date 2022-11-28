import matplotlib.pyplot as plt
import numpy as np
from   utils import getConfigurationByID, cut_area, concat_interms_filled
#from bins.pyocean import get_MLD_1D_temp,get_MLD_1D_dens
import os
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import xarray as xr
import pandas as pd
from operator import itemgetter
from itertools import groupby
import pylab as pl

sns.set_theme(style="whitegrid")

plt.rcParams["figure.figsize"] = 5, 8
plt.rcParams.update({'font.size': 14})

def MyTicks(x, pos):
    'The two args are the value and tick position'
    if pos is not None:
        tick_locs=ax.yaxis.get_majorticklocs()      # Get the list of all tick locations
        str_tl=str(tick_locs).split()[1:-1]         # convert the numbers to list of strings
        p=max(len(i)-i.find('.')-1 for i in str_tl) # calculate the maximum number of non zero digit after "."
        p=max(1,p)                                  # make sure that at least one zero after the "." is displayed
        return "pos:{0}/x:{1:1.{2}f}".format(pos,x,p)


def format_date(x, pos=None):
    return pl.num2date(x).strftime('%Y-%m-%d')



def main(runningDir,exps,years,test=False,statistics=False,suptitle=False):

    interm_tmpl = os.path.join(getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'hvFiles_dir'), '{exp}_{year}_mld.nc')
    conf = getConfigurationByID(os.path.join(runningDir,'conf.yaml'),'mld')
    outdir_plots=os.path.join(conf.outdir.format(plot_dir=getConfigurationByID(os.path.join(runningDir,'conf.yaml'),'plot_dir')),'-'.join(exps))
    os.makedirs(outdir_plots,exist_ok=True)
    ds_all=concat_interms_filled(exps, years, interm_tmpl)
    outname = os.path.join(outdir_plots, f"{years[0]}-{years[-1]}_mld_stats.png")
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)

    ax.xaxis.set_tick_params(rotation=45)
    ax.legend(loc='best', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    for exp in exps:
        print (ds_all)
        ds=ds_all.sel(model=f"{exp}_T")

        #ds_depthBin=ds.groupby_bins('depth', bins=np.arange(int(np.nanmin(ds.depth.values)),int(np.nanmax(ds.depth.values)),1)).mean()


        #ax.set_title(f'{var.capitalize()} {statLong[statAbbrev]} [${umeas[var][statAbbrev]}$]', fontsize=14)
        #ax.set_ylabel(ylabel=f'{statShort} [${umeas[var][statAbbrev]}$]', fontsize=14)
        #ax.set_xlabel(xlabel='')

        ax.plot(ds['month'],ds['mod_mld'].values.T,label=exp)


        #formatter = FuncFormatter(test)
        #ax.xaxis.set_major_formatter(formatter)
    ax.plot(ds['month'],ds['obs_mld'].values.T,c='k',label='argo',linestyle='--')
    ax.legend(loc='best')

    ax.grid(linestyle=':', linewidth=0.5, color='gray')
    ax.invert_yaxis()
    plt.ylabel('Depth[m]')
    plt.tight_layout()

    plt.savefig(outname)
    plt.close()





        # for criterium in conf.criteria:
        #
        #
        #     salinity_bias=[]
        #     salinity_rmse = []
        #     temperature_bias=[]
        #     temperature_rmse = []
        #
        #     basins_name=[]
        #     for year in years:
        #         filesToPlot=[interm_tmpl.format(year=year,exp=f'{exp}_T') for exp in exps]
        #         print (filesToPlot)
        #         nc = xr.open_mfdataset(filesToPlot)
        #         ##try:
        #         #    nc = xr.open_mfdataset(filesToPlot, combine='by_coords')
        #         ##except:
        #         #    continue
        #         for variable in conf.variables:
        #
        #             print ('plotting %s'%variable)
        #
        #             basins_rmse=[]
        #             basins_bias = []
        #             for basin in conf.postproc.area:
        #                 basins_name.append(basin)
        #
        #                 text_bias = [ r"$\bf{Profile}$" +" "+r"$\bf{avg}$"+" "+r"$\bf{0-200m}$"]
        #                 text_rmse=[ r"$\bf{Profile}$"+" "+r"$\bf{avg}$"+" "+r"$\bf{0-200m}$"]
        #
        #                 print('basin %s' % basin)
        #
        #                 rangelimit = conf.postproc.area[basin].box
        #
        #                 regional = cut_area(nc, rangelimit.xmin, rangelimit.xmax,
        #                                 rangelimit.ymin,
        #                                 rangelimit.ymax)
        #
        #                 try:
        #                     result= getBins(regional, bins,conf.postproc.filters.threshold)
        #                 except:
        #                     continue
        #
        #                 nobs=int (np.nansum(result['salinity_nobs'].values[:,0]))
        #
        #                 result['depth'] = xr.DataArray((bins[1:] + bins[:-1]) / 2., dims='depth_bins')
        #                 depths=result['depth']
        #                 models_rmse=[]
        #                 models_bias=[]
        #                 print(result['temperature'].values,depths)
        #
        #                 fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
        #                 fig.set_size_inches(7, 5)
        #                 if suptitle:
        #                     fig.suptitle(basin)
        #
        #                 for i,model  in enumerate(result.model):
        #
        #                     #name=phdNameConv[str(model.data)]
        #                     name = str(model.data)
        #
        #
        #                     ax1.plot(result['%s_bias' % (variable)].T[i], depths,
        #                              label=name,marker='o',  markeredgecolor='w')
        #                     ax2.plot(result['%s_rmse' % (variable)].T[i], depths,
        #                              label=name,marker='o',  markeredgecolor='w')
        #
        #                     text_bias.append('%s: %s'%(name,np.round(np.nanmean(result['%s_bias'% (variable)].T[i][:9]),2)))
        #                     text_rmse.append('%s: %s' % (name, np.round(np.nanmean(result['%s_rmse' % (variable)].T[i][:9]),2)))
        #
        #                     models_bias.append(result['%s_bias' % (variable)].T[i].values)
        #                     models_rmse.append(result['%s_rmse' % (variable)].T[i].values)
        #                 if statistics:
        #                     ax1.annotate('\n'.join(text_bias), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)
        #                     ax2.annotate('\n'.join(text_rmse), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)
        #
        #                 plt.semilogy()
        #                 ax1.legend(loc='lower right', fontsize=8)
        #                 plt.gca().invert_yaxis()
        #
        #                 ax1.set_yticks(bins)
        #                 ax1.set_yticklabels(bins)
        #                 ax2.set_yticks(bins)
        #
        #                 ax1.set_ylabel('Depth[ m]')
        #
        #                 ax1.set_title('Observations: %s'%nobs,fontsize=10,loc='left')
        #                 ax2.set_title('%s - %s'%(year, variable.capitalize()),fontsize=14,loc='right')
        #
        #                 ax1.grid(True, c='silver', lw=1, ls=':')
        #                 ax2.grid(True, c='silver', lw=1, ls=':')
        #
        #                 ax1.set_xlabel('Bias [%s]'%('PSU' if variable=='salinity' else 'degC'))
        #                 ax2.set_xlabel('RMSE')
        #
        #                 plt.savefig((os.path.join(outdir_plots, '%s_%s_%s.png' % (year,basin,variable))))
        #                 plt.close()
        #
        #                 basins_rmse.append(models_rmse)
        #                 basins_bias.append(models_bias)
        #
        #             if variable=='temperature':
        #                 temperature_bias.append(basins_bias)
        #                 temperature_rmse.append(basins_rmse)
        #             elif variable=='salinity':
        #
        #                 salinity_bias.append(basins_bias)
        #                 salinity_rmse.append(basins_rmse)
        #
        #     # years, basins, models depth
        #     print (np.array(temperature_rmse).shape)


if __name__ == '__main__':

    main(exps,years,test=True)



