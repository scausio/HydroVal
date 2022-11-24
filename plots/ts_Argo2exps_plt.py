import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from bins.utils import getConfigurationByID, cut_area, getBins, annotateCumulative
import os
from matplotlib.lines import Line2D

plt.rcParams["figure.figsize"] = 5, 8
plt.rcParams.update({'font.size': 14})


def main(exps,years):
    colors=['b','g','orange','r','m','k']
    print('*** TIMESERIES ARGO 2 EXPS PLOTTING ***')
    conf = getConfigurationByID('conf.yaml', 'timeseriesArgo')
    interm_tmpl = os.path.join(getConfigurationByID('conf.yaml', 'hvFiles_dir'), '{exp}_{year}_argo.nc')
    bins = np.array(list(map(float, conf.postproc.bins)))
    x_labels = ['%s-%s' % (int(i), int(j)) for i, j in zip(bins[:-1], bins[1:])]
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')),
                                '-'.join(exps))
    os.makedirs(outdir_plots, exist_ok=True)

    name_1 = exps[0] #MUST BE THE UNCOUPLED#os.path.basename(conf.dataset['path_1']).replace('_{year}.nc', '') #phdNameConv[os.path.basename(conf.dataset['path_1']).replace('_{year}.nc', '')]
    name_2 = exps[1]##MUST BE THE COUPLED#os.path.basename(conf.dataset['path_2']).replace('_{year}.nc', '') #phdNameConv[os.path.basename(conf.dataset['path_2']).replace('_{year}.nc', '')]

    for variable in conf.variables:
        print ('plotting %s'%variable)
        for basin in conf.postproc.area:
            print('basin %s' % basin)

            ds_bias_1=[]
            ds_rmse_1 = []
            ds_bias_2 = []
            ds_rmse_2 = []
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
                    nc_1 = xr.open_dataset(interm_tmpl.format(year=year, exp=f'{exps[0]}_T'))
                    nc_2 = xr.open_dataset(interm_tmpl.format(year=year, exp=f'{exps[1]}_T'))
                except:
                    obs.append(0)
                    ds_bias_1.append(np.nan*bins[1:])
                    ds_rmse_1.append(np.nan * bins[1:])
                    ds_bias_2.append(np.nan*bins[1:])
                    ds_rmse_2.append(np.nan * bins[1:])
                    continue
                rangelimit = conf.postproc.area[basin].box

                regional_1 = cut_area(nc_1, rangelimit.xmin, rangelimit.xmax,
                                    rangelimit.ymin,
                                    rangelimit.ymax)

                regional_2 = cut_area(nc_2, rangelimit.xmin, rangelimit.xmax,
                                    rangelimit.ymin,
                                    rangelimit.ymax)
                try:
                    result_1 = getBins(regional_1, bins,conf.postproc.filters.threshold)
                    obs.append(int(np.nansum(result_1['salinity_nobs'].values[:, 0])))
                    result_1.rename_vars({'salinity_nobs': 'nobs'}).drop_vars('temperature_nobs').to_dataframe()

                    result_2 = getBins(regional_2, bins,conf.postproc.filters.threshold)
                    result_2.rename_vars({'salinity_nobs': 'nobs'}).drop_vars('temperature_nobs').to_dataframe()
                except:

                    obs.append(0)
                    ds_bias_1.append(np.nan*bins[1:])
                    ds_rmse_1.append(np.nan * bins[1:])
                    ds_bias_2.append(np.nan*bins[1:])
                    ds_rmse_2.append(np.nan * bins[1:])

                    continue


                result_1['depth'] = xr.DataArray((bins[1:] + bins[:-1]) / 2., dims='depth_bins')
                result_2['depth'] = xr.DataArray((bins[1:] + bins[:-1]) / 2., dims='depth_bins')

                ds_bias_1.append(result_1['%s_bias' % (variable)].isel(model=0).data)
                ds_rmse_1.append(result_1['%s_rmse' % (variable)].isel(model=0).data)

                ds_bias_2.append(result_2['%s_bias' % (variable)].isel(model=0).data)
                ds_rmse_2.append(result_2['%s_rmse' % (variable)].isel(model=0).data)

            print (obs)
            ds_rmse_1=np.array(ds_rmse_1).T
            ds_bias_1=np.array(ds_bias_1).T

            print (ds_rmse_1.shape)

            ds_rmse_2=np.array(ds_rmse_2).T
            ds_bias_2=np.array(ds_bias_2).T

            ax4.bar(years,obs,facecolor='k',alpha=0.2)

            ax4.set_ylabel('Observations')

            custom_labels_name=[]
            custom_labels_props = []

            mean_bias1=['BIAS %s[{v}]= '%name_1.split('-')[-1]]
            mean_bias2 = ['BIAS %s[{v}]= '%name_2.split('-')[-1]]
            mean_rmse1=['RMSE %s[{v}]= '%name_1.split('-')[-1]]
            mean_rmse2 = ['RMSE %s[{v}]= '%name_2.split('-')[-1]]

            for i,j in enumerate(x_labels):

                marker_style_unc = dict(color=colors[i], linestyle='-', marker='o',
                                    markersize=8, markerfacecoloralt=colors[i])

                marker_style_c = dict(color=colors[i], linestyle=':', marker='D',
                                    markersize=8, markerfacecoloralt=colors[i])

                ax1.plot( list(years),ds_bias_1[i],**marker_style_unc )
                ax2.plot( list(years),ds_rmse_1[i],**marker_style_unc)

                ax1.plot( list(years),ds_bias_2[i],**marker_style_c)
                ax2.plot( list(years),ds_rmse_2[i],**marker_style_c)

                custom_labels_props.append(Line2D([0], [0], color=colors[i], lw=8))
                custom_labels_name.append(j)

                mean_bias1.append(np.nanmean(ds_bias_1[i]))
                mean_bias2.append(np.nanmean(ds_bias_2[i]))

                mean_rmse1.append(np.nanmean(ds_rmse_1[i]))
                mean_rmse2.append(np.nanmean(ds_rmse_2[i]))

            custom_labels_props.append(Line2D([0], [0], color='k', markerfacecolor='k',markeredgecolor='k',marker='o',linestyle='-'))
            custom_labels_name.append(name_1)
            custom_labels_props.append(Line2D([0], [0], color='k', markerfacecolor='k',markeredgecolor='k',marker='D',linestyle=':'))
            custom_labels_name.append(name_2)
            #ax4.fill_between(list(years),obs,facecolor='k',alpha=0.25)

            #ax1.legend(title='Depth [m]',loc='best', fontsize=10)
            ax1.legend(custom_labels_props, custom_labels_name,
                           fontsize=10, loc='best',title='Depth [m]')
            ax1.set_xticks(years)
            #ax1.set_xticklabels([str(int(y))for y in years],rotation=30)
            ax2.set_xticklabels([str(int(y)) for y in years], rotation=40,fontsize=10)
            ax2.set_xlabel('Years')

            #ax1.set_title(f'Observations: {nobs}',fontsize=10,loc='left')

            ax1.grid(True, c='silver', lw=1, ls=':')
            ax2.grid(True, c='silver', lw=1, ls=':')

            ax1.set_ylabel('Bias [%s]'%('PSU' if variable=='salinity' else 'degC'))
            ax2.set_ylabel('RMSE')

            annotateCumulative(ax1, mean_bias1, colors)
            annotateCumulative(ax1, mean_bias2, colors, yshift=-0.03)
            annotateCumulative(ax2, mean_rmse1, colors)
            annotateCumulative(ax2, mean_rmse2, colors, yshift=-0.03)

            fig.tight_layout()

            plt.savefig((os.path.join(outdir_plots, f'{name_1}_{name_2}_{basin}_{variable}.png')))
            plt.close()


if __name__ == '__main__':
    main()



