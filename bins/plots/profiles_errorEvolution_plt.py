
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from utils import getConfigurationByID, cut_area, getBins
import os
import seaborn as sns

sns.set_theme(style="whitegrid")


plt.rcParams["figure.figsize"] = 5, 8
plt.rcParams.update({'font.size': 14})


def main(runningDir,exps,years,suptitle=False):
    print ('*** PROFILE ERROR PLOTTING ***')
    interm_tmpl = os.path.join(getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'hvFiles_dir'), '{exp}_{year}_argo.nc')
    conf = getConfigurationByID(os.path.join(runningDir,'conf.yaml'),'profiles')
    bins = np.array(list(map(float, conf.postproc.bins)))
    outdir_plots=os.path.join(conf.outdir.format(plot_dir=getConfigurationByID(os.path.join(runningDir,'conf.yaml'),'plot_dir')),'-'.join(exps))
    os.makedirs(outdir_plots,exist_ok=True)

    basins_name=[]

    for variable in conf.variables:
        print('plotting %s' % variable)
        for basin in conf.postproc.area:
            basins_name.append(basin)
            for exp in exps:
                fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
                fig.set_size_inches(7, 5)
                if suptitle:
                    fig.suptitle(basin)

                for year in years:
                    filesToPlot = [interm_tmpl.format(year=year, exp=f'{exp}_T') for exp in exps]
                    print(filesToPlot)
                    nc = xr.open_mfdataset(filesToPlot).isel(model=0)

                    rangelimit = conf.postproc.area[basin].box

                    regional = cut_area(nc, rangelimit.xmin, rangelimit.xmax,
                                    rangelimit.ymin,
                                    rangelimit.ymax)

                    try:
                        result= getBins(regional, bins,conf.postproc.filters.threshold)
                    except:
                        continue


                    result['depth'] = xr.DataArray((bins[1:] + bins[:-1]) / 2., dims='depth_bins')
                    depths=result['depth']

                    print(result['temperature'].values,depths)

                    ax1.plot(result['%s_bias' % (variable)].T, depths,marker='o',  markeredgecolor='w',
                             label=year)
                    ax2.plot(result['%s_rmse' % (variable)].T, depths,marker='o',  markeredgecolor='w',
                             label=year)

            plt.semilogy()
            ax1.legend(loc='lower right', fontsize=8)
            plt.gca().invert_yaxis()

            ax1.set_yticks(bins)
            ax1.set_yticklabels(bins)
            ax2.set_yticks(bins)

            ax1.set_ylabel('Depth[ m]')

            ax2.set_title('%s - %s'%(exp, variable.capitalize()),fontsize=14,loc='right')

            ax1.grid(True, c='silver', lw=1, ls=':')
            ax2.grid(True, c='silver', lw=1, ls=':')

            ax1.set_xlabel('Bias [%s]'%('PSU' if variable=='salinity' else 'degC'))
            ax2.set_xlabel('RMSE')

            plt.savefig((os.path.join(outdir_plots, f'errorEvolution_{exp}_{variable}_{years[0]}-{years[-1]}.png')))
            plt.close()



if __name__ == '__main__':
    # phdNameConv = {}
    # phdNameConv['bs-phd_5.8.0']= 'H1'
    # phdNameConv['bs-phd_5.5.2']= 'H2'
    # phdNameConv['bs-phd_5.6.2']= 'H3'
    # phdNameConv['bs-simu_1.0']= 'bs-simu_1.0'
    # phdNameConv['bs-phd_4.0.1']= 'H0'
    # phdNameConv['bs-phd_5.2.2'] = 'H4'
    # phdNameConv['uncoup_longRun']='H0'
    # phdNameConv['coupl_longRun'] = 'H4'
    #
    # phdNameConv['bs-phd_6.0.1']= 'H0'
    # phdNameConv['bs-phd_5.10.2']= 'H1'
    # phdNameConv['bs-phd_5.11.2']= 'H2'
    # phdNameConv['bs-phd_5.12.2'] = 'H3'
    # phdNameConv['bs-phd_5.8.2']= 'H4'
    # print (phdNameConv)


    main()



