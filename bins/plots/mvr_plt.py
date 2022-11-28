import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from utils import getConfigurationByID, cut_area, getBins,umeas,stats_longName
import os
import pandas as pd
import seaborn as sns
from scipy.stats import linregress,pearsonr
from matplotlib.ticker import MaxNLocator
import matplotlib.markers as mrk
sns.set_theme(style="whitegrid")


def plotCov(exp, df, var, year, outdir, conf, statAbbrev,umeas,statLong,regression=False, statistics=False):
    print(f'plotting {year} {var} covariance')

    ylims=conf[statAbbrev][var].ylims
    outname = os.path.join(outdir, f"{exp}_{year}_{var}_cov.png")
    text_stats = [r"$\bf{Avg:}$" + " "]
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 8)
    ax.set_title(f'{var.capitalize()} {statLong[statAbbrev]} [${umeas[var][statAbbrev]}$]', fontsize=14)
    ax=sns.scatterplot(x=df[f'model_{var}'],y=df[var])
    ax.set_ylabel(ylabel=exp, fontsize=14)
    ax.set_xlabel(xlabel='observations',fontsize=14)
    if statistics:
        text_stats.append('%s: %s' % (exp, np.round(np.nanmean(df[var].values), 2)))
        text_stats.append('%s: %s' % ('obs', np.round(np.nanmean(df[f'model_{var}'].values), 2)))
        plt.annotate('\n'.join(text_stats), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=10)

    if regression:
        model=df[f'{var}'].values[np.logical_not(np.isnan(df[f'{var}'].values))]
        obs= df[f'model_{var}'].values[np.logical_not(np.isnan(df[f'model_{var}'].values))]
        corr, _ = pearsonr(obs, model)
        slope, intercept, rvalue, pvalue, stderr = linregress( obs,model)
        plt.text(0.8, 0.08, "y = {m}x + {q}\n$\\rho$:{p}\n".format(m=np.round(slope, 2), q=np.round(intercept, 2),p=np.round(corr,2)),
                 verticalalignment='top',
              size=10, style='italic',transform = ax.transAxes)
        #slope = 1 + (1 - slope)
        ax.plot([0, np.max(np.max([model,obs]))],[0, np.max(np.max([model,obs])) * slope],c='r',label='regression')
        ax.plot([0, np.max(np.max([model,obs]))],[0, np.max(np.max([model,obs]))],c='gray',linestyle='-.', label ='best fit')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.savefig(outname)
    plt.close()

def plotStats(exp, df, var,obs, year, outdir, conf, statAbbrev,umeas,statLong, statistics=False):
    print(f'plotting {year} {var} {statAbbrev}')

    statShort=statAbbrev

    ylims=conf[statAbbrev][var].ylims
    outname = os.path.join(outdir, f"{exp}_{year}_{var}_{statShort}.png")
    text_stats = [r"$\bf{Avg:}$" + " "]

    fig, ax = plt.subplots()
    fig.set_size_inches(12, 6)


    ax.xaxis.set_tick_params(rotation=45)
    ax.legend(loc='best', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.set_title(f'{var.capitalize()} {statLong[statAbbrev]} [${umeas[var][statAbbrev]}$]', fontsize=14)
    ax.set_ylabel(ylabel=f'{statShort} [${umeas[var][statAbbrev]}$]', fontsize=14)
    ax.set_xlabel(xlabel='')

    if statAbbrev in ['BIAS','MSE']:
        #ax=sns.lineplot(data=df, label=exp, marker='o',ax=ax,zorder=100)
        ax.plot(df, label=exp, marker='o',zorder=2.6,markeredgecolor='w')
        pass
    else:
        ax.plot(df[var], label=exp, marker='o',zorder=2.6,markeredgecolor='w')
        ax.plot(df[f'model_{var}'],label='obs',marker='o',linestyle='dashed',zorder=2.5,markeredgecolor='w')

    ax.legend(loc='best')

    ax.grid(linestyle=':', linewidth=0.5, color='gray')


    # ax2 = ax.twinx()
    # #ax2.bar(obs.index, obs, facecolor='gray', alpha=0.5,zorder=0)
    # #ax2.plot(obs,color='gray',alpha=0.3)
    # #ax2.fill_between(df.index, np.zeros_like(obs), obs,facecolor='gray',alpha=0.5)
    # ax2.set_ylabel("observations", color="gray", fontsize=14)
    # ax2.yaxis.label.set_color('gray')
    # ax2.tick_params(axis='y', colors='gray')
    # ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    # ax2.grid(False)


    if type(ylims):
        ax.set_ylim(ylims)
    if statistics:
        if statAbbrev in ['BIAS', 'MSE']:

            text_stats.append('%s: %s' % (exp, np.round(np.nanmean(df.values), 2)))
        else:
            text_stats.append('%s: %s' % (exp, np.round(np.nanmean(df[var].values), 2)))
            text_stats.append('%s: %s' % ('obs', np.round(np.nanmean(df[f'model_{var}'].values), 2)))
        plt.annotate('\n'.join(text_stats), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=10)


    plt.tight_layout()
    plt.savefig(outname)
    plt.close()


def difference(df):
    temp_dif = df.temperature - df.model_temperature
    sal_dif = df.salinity - df.model_salinity
    return temp_dif, sal_dif

def bias_daily(dif):
    return dif.groupby([pd.Grouper(level='time', freq='1D')]).mean()

def mse_daily(dif):
    sqrd_dif=dif**2
    return np.sqrt(sqrd_dif.groupby([pd.Grouper(level='time', freq='1D')]).mean())


def mvr(runningDir,exp, intermediate, yearName,regression,statistics):
    conf = getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'mvr').plot_conf
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'plot_dir')), exp)
    os.makedirs(outdir_plots, exist_ok=True)

    ds = intermediate.where((intermediate.depth > conf.zmin) & (intermediate.depth < conf.zmax))
    ds = ds.dropna('obs')

    df = ds.to_dataframe().set_index('time')
    df_temp = df[["temperature", "model_temperature"]]
    df_sal = df[["salinity", "model_salinity"]]

    df_dailyTemp = df_temp.groupby([pd.Grouper(level='time', freq='1D')])
    df_dailySal = df_sal.groupby([pd.Grouper(level='time', freq='1D')])

    obs=df_dailyTemp.temperature.count()

    tempDif, salDif = difference(df)
    bias_T = bias_daily(tempDif)
    bias_S = bias_daily(salDif)
    mse_T = mse_daily(tempDif)
    mse_S = mse_daily(salDif)

    plotStats(exp, df_dailySal.var(), 'salinity',obs,  yearName, outdir_plots, conf, 'var', umeas, stats_longName,
              statistics=statistics)
    plotStats(exp, df_dailyTemp.var(), 'temperature',obs,  yearName, outdir_plots, conf, 'var', umeas, stats_longName,
              statistics=statistics)

    plotStats(exp, df_dailySal.std(), 'salinity',obs,  yearName, outdir_plots, conf, 'std', umeas, stats_longName,
              statistics=statistics)
    plotStats(exp, df_dailyTemp.std(), 'temperature',obs,  yearName, outdir_plots, conf, 'std', umeas, stats_longName,
              statistics=statistics)

    plotStats(exp, df_dailySal.mean(), 'salinity',obs,  yearName, outdir_plots, conf, 'mean', umeas, stats_longName,
              statistics=statistics)
    plotStats(exp, df_dailyTemp.mean(), 'temperature',obs,  yearName, outdir_plots, conf, 'mean', umeas, stats_longName,
              statistics=statistics)

    plotStats(exp, bias_S, 'salinity',obs,  yearName, outdir_plots, conf, 'BIAS', umeas, stats_longName, statistics=statistics)
    plotStats(exp, bias_T, 'temperature',obs,  yearName, outdir_plots, conf, 'BIAS', umeas, stats_longName,
              statistics=statistics)

    plotStats(exp, mse_S, 'salinity',obs,  yearName, outdir_plots, conf, 'MSE', umeas, stats_longName, statistics=statistics)
    plotStats(exp, mse_T, 'temperature',obs, yearName,  outdir_plots, conf, 'MSE', umeas, stats_longName, statistics=statistics)

    plotCov(exp, df_dailySal.cov(), 'salinity', yearName, outdir_plots, conf, 'cov', umeas, stats_longName,
            regression=regression, statistics=statistics)
    plotCov(exp, df_dailyTemp.cov(), 'temperature', yearName, outdir_plots, conf, 'cov', umeas, stats_longName,
            regression=regression, statistics=statistics)


def main(runningDir,expsName,years,regression=False,statistics=False):
    print ('*** MVR PLOTTING ***')
    for exp in expsName:
        files=[]
        for year in years:
            interm_tmpl = os.path.join(getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'hvFiles_dir'), f'{exp}_T_{year}_argo.nc')
            intermediate=xr.open_dataset(interm_tmpl).isel(model=0)
            mvr(runningDir,exp, intermediate, year,regression,statistics)
            files.append(interm_tmpl)
        if len(years)>1:
            print(years)
            intermediate = xr.open_mfdataset(os.path.join(getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'hvFiles_dir'), f'{exp}_T_*_argo.nc')).isel(model=0)
            mvr(runningDir,exp, intermediate, f'{years[0]}-{years[-1]}', regression, statistics)



