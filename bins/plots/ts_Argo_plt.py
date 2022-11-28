
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import os
from utils import getConfigurationByID, cut_area, getBins

plt.rcParams["figure.figsize"] = 5, 8
plt.rcParams.update({'font.size': 14})

def main(runningDir,exps,years):
    print('*** TIMESERIES ARGO PLOTTING ***')
    conf = getConfigurationByID(os.path.join(runningDir,'conf.yaml'),'timeseriesArgo')
    interm_tmpl = os.path.join(getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'hvFiles_dir'), '{exp}_{year}_argo.nc')
    bins = np.array(list(map(float, conf.postproc.bins)))

    x_labels = ['%s-%s' % (int(i), int(j)) for i, j in zip(bins[:-1], bins[1:])]
    print(bins)
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'plot_dir')),
                                '-'.join(exps))
    os.makedirs(outdir_plots,exist_ok=True)
    for exp in exps:
        for variable in conf.variables:
            print ('plotting %s'%variable)
            for basin in conf.postproc.area:
                print('basin %s' % basin)
                ds_bias=[]
                ds_rmse = []
                obs=[]
                fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

                ax4 = ax2.twinx()
                fig.set_size_inches(11, 10)

                fig.suptitle(basin)
                ax1.set_title('%s' % (variable.capitalize()), fontsize=14, loc='right')
                ax1.set_title('CMEMS-NSITU_OBSERVATIONS', fontsize=8, loc='left')

                for year in years:
                    print('year %s' % year)
                    year=str(year)

                    try:
                        print (interm_tmpl.format(year=year,exp=f'{exp}_T'))
                        nc=xr.open_dataset(interm_tmpl.format(year=year,exp=f'{exp}_T'))
                    except:
                        obs.append(0)
                        ds_bias.append(np.nan*bins[1:])
                        ds_rmse.append(np.nan * bins[1:])
                        continue
                    rangelimit = conf.postproc.area[basin].box

                    regional = cut_area(nc, rangelimit.xmin, rangelimit.xmax,
                                        rangelimit.ymin,
                                        rangelimit.ymax)


                    try:
                        result = getBins(regional, bins,conf.postproc.filters.threshold)
                        obs.append(int(np.nansum(result['salinity_nobs'].values[:, 0])))
                        result.rename_vars({'salinity_nobs': 'nobs'}).drop_vars('temperature_nobs').to_dataframe()
                    except:

                        obs.append(0)
                        ds_bias.append(np.nan*bins[1:])
                        ds_rmse.append(np.nan * bins[1:])

                        continue


                    result['depth'] = xr.DataArray((bins[1:] + bins[:-1]) / 2., dims='depth_bins')

                    ds_bias.append(result['%s_bias' % (variable)].isel(model=0).data)
                    ds_rmse.append(result['%s_rmse' % (variable)].isel(model=0).data)

                print (obs)
                ds_rmse=np.array(ds_rmse).T
                ds_bias=np.array(ds_bias).T

                ax4.bar(years,obs,facecolor='k',alpha=0.2)
                ax4.set_ylabel('Observations')


                for i,j in enumerate(x_labels):
                    print (i)
                    ax1.plot( list(years),ds_bias[i],'.-',
                             label=j )
                    ax2.plot( list(years),ds_rmse[i],'.-',
                             label=j)
                #ax4.fill_between(list(years),obs,facecolor='k',alpha=0.25)

                ax1.legend(title='Depth [m]',loc='best', fontsize=12)

                ax1.set_xticks(years)
                #ax1.set_xticklabels([str(int(y))for y in years],rotation=30)
                ax2.set_xticklabels([str(int(y)) for y in years], rotation=40,fontsize=10)
                ax2.set_xlabel('Years')


                #ax1.set_title(f'Observations: {nobs}',fontsize=10,loc='left')


                ax1.grid(True, c='silver', lw=1, ls=':')
                ax2.grid(True, c='silver', lw=1, ls=':')

                ax1.set_ylabel('Bias [%s]'%('PSU' if variable=='salinity' else 'degC'))
                ax2.set_ylabel('RMSE')
                fig.tight_layout()
                #plt.show()
                plt.savefig(os.path.join(outdir_plots, f'{exp}_{basin}_{variable}.png'))
                plt.close()

if __name__ == '__main__':

    main()



