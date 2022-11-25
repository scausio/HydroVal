
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from utils import getConfigurationByID, cut_area, getBins
import os
import seaborn as sns

sns.set_theme(style="whitegrid")

def globalPlot(bias, rmse, depths,years, exps_name, basins_name, variable, outdir_plots, bins,statistics,suptitle):
    buffer_rmse = np.array(rmse).transpose((1, 2, 0, 3))
    buffer_bias = np.array(bias).transpose((1, 2, 0, 3))

    for i, basin in enumerate(buffer_rmse):
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
        fig.set_size_inches(7, 5)
        if suptitle:
            fig.suptitle(basins_name[i])

        text_bias = [r"$\bf{Profile}$" + " " + r"$\bf{avg}$" + " " + r"$\bf{0-200m}$"]
        text_rmse = [r"$\bf{Profile}$" + " " + r"$\bf{avg}$" + " " + r"$\bf{0-200m}$"]
        for j, exp_val in enumerate(basin):
            name=exps_name[j]

            text_bias.append('%s: %s' % (name, np.round(np.nanmean(buffer_bias[i][j][:,:9]), 2)))
            text_rmse.append('%s: %s' % (name, np.round(np.nanmean(exp_val[:,:9]), 2)))
            print (depths.values,np.nanmean(buffer_bias[i][j], axis=0))

            #sns.lineplot(data={'bias':np.nanmean(buffer_bias[i][j], axis=0),'depth':depths.values},x='bias',y='depth', linewidth=2, label=name, marker="o",ax=ax1)
            #sns.lineplot(data={'rmse':np.nanmean(exp_val, axis=0),'depth':depths.values},x='rmse',y='depth', linewidth=2, label=name, marker="o",ax=ax2)
            ax1.plot(np.nanmean(buffer_bias[i][j], axis=0), depths, marker='o',  markeredgecolor='w',label=name,linewidth=2)
            ax2.plot(np.nanmean(exp_val, axis=0), depths, '.-', label=name,linewidth=2,marker='o',  markeredgecolor='w')
        if statistics:
            ax1.annotate('\n'.join(text_bias), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)
            ax2.annotate('\n'.join(text_rmse), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)
        plt.semilogy()
        ax1.legend(loc='lower right', fontsize=14)
        plt.gca().invert_yaxis()

        ax1.set_yticks(bins)
        ax1.set_yticklabels(bins)
        ax2.set_yticks(bins)

        ax1.set_ylabel('Depth[ m]')

        ax2.set_title(variable, fontsize=16, loc='right')
        ax1.set_title(f'[{years[0]}-{years[-1]}]', fontsize=16, loc='left')
        # plt.legend(loc='best')
        ax1.grid(True, c='silver', lw=1, ls=':')
        ax2.grid(True, c='silver', lw=1, ls=':')

        ax1.set_xlabel('Bias [%s]' % ('PSU' if variable == 'Salinity' else 'degC'))
        ax2.set_xlabel('RMSE')
        #plt.show()
        plt.savefig((os.path.join(outdir_plots, 'allYears_%s_%s.png' % (basins_name[i], variable))))
        plt.close()

plt.rcParams["figure.figsize"] = 5, 8
plt.rcParams.update({'font.size': 14})


def main(exps,years,statistics=False,suptitle=False):
    print ('*** PROFILES PLOTTING ***')

    interm_tmpl = os.path.join(getConfigurationByID('conf.yaml', 'hvFiles_dir'), '{exp}_{year}_argo.nc')
    conf = getConfigurationByID('conf.yaml','profiles')
    bins = np.array(list(map(float, conf.postproc.bins)))

    outdir_plots=os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml','plot_dir')),'-'.join(exps))
    os.makedirs(outdir_plots,exist_ok=True)

    salinity_bias=[]
    salinity_rmse = []
    temperature_bias=[]
    temperature_rmse = []

    basins_name=[]
    for year in years:
        filesToPlot=[interm_tmpl.format(year=year, exp=f'{exp}_T') for exp in exps]
        print (filesToPlot)
        nc = xr.open_mfdataset(filesToPlot)

        for variable in conf.variables:

            print ('plotting %s'%variable)

            basins_rmse=[]
            basins_bias = []
            for basin in conf.postproc.area:
                basins_name.append(basin)

                text_bias = [ r"$\bf{Profile}$" +" "+r"$\bf{avg}$"+" "+r"$\bf{0-200m}$"]
                text_rmse=[ r"$\bf{Profile}$"+" "+r"$\bf{avg}$"+" "+r"$\bf{0-200m}$"]

                print('basin %s' % basin)

                rangelimit = conf.postproc.area[basin].box

                regional = cut_area(nc, rangelimit.xmin, rangelimit.xmax,
                                rangelimit.ymin,
                                rangelimit.ymax)

                try:
                    result= getBins(regional, bins,conf.postproc.filters.threshold)
                except:
                    continue

                nobs=int (np.nansum(result['salinity_nobs'].values[:,0]))

                result['depth'] = xr.DataArray((bins[1:] + bins[:-1]) / 2., dims='depth_bins')
                depths=result['depth']
                models_rmse=[]
                models_bias=[]
                print(result['temperature'].values,depths)

                fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
                fig.set_size_inches(7, 5)
                if suptitle:
                    fig.suptitle(basin)

                for i,model  in enumerate(result.model):

                    #name=phdNameConv[str(model.data)]
                    name = str(model.data)


                    ax1.plot(result['%s_bias' % (variable)].T[i], depths,
                             label=name,marker='o',  markeredgecolor='w')
                    ax2.plot(result['%s_rmse' % (variable)].T[i], depths,
                             label=name,marker='o',  markeredgecolor='w')

                    text_bias.append('%s: %s'%(name,np.round(np.nanmean(result['%s_bias'% (variable)].T[i][:9]),2)))
                    text_rmse.append('%s: %s' % (name, np.round(np.nanmean(result['%s_rmse' % (variable)].T[i][:9]),2)))

                    models_bias.append(result['%s_bias' % (variable)].T[i].values)
                    models_rmse.append(result['%s_rmse' % (variable)].T[i].values)
                if statistics:
                    ax1.annotate('\n'.join(text_bias), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)
                    ax2.annotate('\n'.join(text_rmse), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)

                plt.semilogy()
                ax1.legend(loc='lower right', fontsize=8)
                plt.gca().invert_yaxis()

                ax1.set_yticks(bins)
                ax1.set_yticklabels(bins)
                ax2.set_yticks(bins)

                ax1.set_ylabel('Depth[ m]')

                ax1.set_title('Observations: %s'%nobs,fontsize=10,loc='left')
                ax2.set_title('%s - %s'%(year, variable.capitalize()),fontsize=14,loc='right')

                ax1.grid(True, c='silver', lw=1, ls=':')
                ax2.grid(True, c='silver', lw=1, ls=':')

                ax1.set_xlabel('Bias [%s]'%('PSU' if variable=='salinity' else 'degC'))
                ax2.set_xlabel('RMSE')

                plt.savefig((os.path.join(outdir_plots, '%s_%s_%s.png' % (year,basin,variable))))
                plt.close()

                basins_rmse.append(models_rmse)
                basins_bias.append(models_bias)

            if variable=='temperature':
                temperature_bias.append(basins_bias)
                temperature_rmse.append(basins_rmse)
            elif variable=='salinity':

                salinity_bias.append(basins_bias)
                salinity_rmse.append(basins_rmse)

    # years, basins, models depth
    print (np.array(temperature_rmse).shape)

    globalPlot(temperature_bias,temperature_rmse,depths,years, exps,basins_name, 'Temperature',outdir_plots,bins,statistics,suptitle)
    globalPlot(salinity_bias, salinity_rmse, depths,years, exps, basins_name, 'Salinity', outdir_plots, bins,statistics,suptitle)

if __name__ == '__main__':

    main()



