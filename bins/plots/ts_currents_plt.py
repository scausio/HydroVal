from  utils import getConfigurationByID
import windrose
import os
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import numpy as np
sns.set_theme(style="whitegrid")

def ticker(years,var):
    if len(years) == 1:
        x_label = ['01-Jan-%s' % years[0], '01-Feb-%s' % years[0], '01-Mar-%s' % years[0], '01-Apr-%s' % years[0],
                   '01-May-%s' % years[0], '01-Jun-%s' % years[0],
                   '01-Jul-%s' % years[0], '01-Aug-%s' % years[0], '01-Sep-%s' % years[0], '01-Oct-%s' % years[0],
                   '01-Nov-%s' % years[0], '01-Dec-%s' % years[0]]
        x_ticks = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    elif len(years)<5:
        x_label = []
        for y in years:
            x_label.append('Jan %s' % y)
            x_label.append('Jun %s' % y)
        x_ticks = [int(i) for i in np.linspace(0, len(var), len(years)*2,endpoint=False)]
    elif len(years) < 10:
        x_label = []
        for y in years:
            x_label.append('Jan %s' % y)
        x_ticks = [int(i) for i in np.linspace(0, len(var), 8,endpoint=False)]
    else:
        x_label = []
        for y in years:
            x_label.append('Jan %s' % y)
        x_ticks = [int(i) for i in np.linspace(0, len(var), 8,endpoint=False)]
    return x_ticks,x_label

def degDifference(a,b):
    ddeg=a-b
    ddeg[ddeg > 180] -= 180
    ddeg[ddeg <- 180] += 180
    #(ddeg + 180) % 360 - 180
    print (ddeg)
    return ddeg


def computeSpeed(u, v):
    return np.sqrt(u ** 2 + v ** 2)


def computeDirection(u, v):
    deg = np.rad2deg(np.arctan2(v, u))
    deg[deg < 0] += 360
    deg[deg > 360] -= 360

    return deg

def getDifference(model,obs):
    return model-obs

def getBias(diff):
    return np.nanmean(diff,axis=1)

def getRMSE(diff):
    return  np.nanmean(np.sqrt(diff**2),axis=1)

def plotTimeseries(exps,years,interm_base,outdir_plots,timeAveraging):
    fig1, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    fig1.set_size_inches(8, 5)



    fig2, (ax3, ax4) = plt.subplots(2, 1, sharex=True)
    fig2.set_size_inches(8, 5)
    if timeAveraging in [None, 'no','none', 'No','NO', False]:
        fig1.suptitle(f'BIAS Currents at 2.5m ')
        fig2.suptitle('RMSE Currents at 2.5m ')
        timeFreq=False
    else:
        fig1.suptitle(f'BIAS Currents at 2.5m - {timeAveraging} mean')
        fig2.suptitle(f'RMSE Currents at 2.5m - {timeAveraging} mean')
        timeFreq = True
    text_bias_sp = [r"$\bf{avg}$"]
    text_bias_dir = [r"$\bf{avg}$"]
    text_rmse_sp = [r"$\bf{avg}$"]
    text_rmse_dir = [r"$\bf{avg}$"]

    for exp in exps:

        buffer=[]
        for year in years:
            buffer.append( xr.open_dataset(os.path.join(interm_base, f"{exp}_{year}_uvMOOR.nc")))
        ds = xr.concat(buffer, dim='TIME')
        ds=ds.transpose("TIME", "station")
        print (ds)
        if timeFreq:
            if timeAveraging not in ['daily','monthly','yearly']:
                exit('please check timeseries_timeAveraging variable in conf.yaml')
            else:
                if timeAveraging =='daily':
                    ds=ds.resample(TIME="d").mean(skipna=True)
                elif timeAveraging=='monthly':
                    ds = ds.resample(TIME="m").mean(skipna=True)
                else:
                    ds = ds.resample(TIME="y").mean(skipna=True)
        print (ds)

        u = ds.mod_u.values
        v = ds.mod_v.values

        model_speed = computeSpeed(u, v)
        model_direction = computeDirection(u, v)-180

        moor_direction=ds.dir.values-180
        print (np.nanmin(model_direction),np.nanmax(model_direction),np.nanmin(moor_direction),np.nanmax(moor_direction))
        speed_diff=getDifference(model_speed, ds.speed.values)
        dir_diff = degDifference(model_direction, moor_direction)
        mskSpikes = np.abs(speed_diff) > 0.6
        speed_diff[mskSpikes]=np.nan
        dir_diff[mskSpikes]=np.nan

        bias_speed=getBias(speed_diff)

        print (dir_diff.shape)

        bias_dir = getBias(dir_diff)

        rmse_speed=getRMSE(speed_diff)
        rmse_dir = getRMSE(dir_diff)

        ax1.plot(bias_speed, label=exp,marker='o',  markeredgecolor='w')
        ax2.plot(bias_dir, label=exp,marker='o',  markeredgecolor='w')

        ax3.plot(rmse_speed, label=exp,marker='o',  markeredgecolor='w')
        ax4.plot(rmse_dir, label=exp,marker='o',  markeredgecolor='w')


        text_bias_sp.append('%s: %s' % (exp, np.round(np.nanmean(bias_speed), 3)))
        text_bias_dir.append('%s: %s' % (exp, np.round(np.nanmean(bias_dir), 3)))
        text_rmse_sp.append('%s: %s' % (exp, np.round(np.nanmean(rmse_speed), 3)))
        text_rmse_dir.append('%s: %s' % (exp, np.round(np.nanmean(rmse_dir), 3)))

    ax1.annotate('\n'.join(text_bias_sp), xy=(0.05, 0.05), xycoords='axes fraction', fontsize=7)
    ax2.annotate('\n'.join(text_bias_dir), xy=(0.05, 0.05), xycoords='axes fraction', fontsize=7)

    ax3.annotate('\n'.join(text_rmse_sp), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)
    ax4.annotate('\n'.join(text_rmse_dir), xy=(0.05, 0.8), xycoords='axes fraction', fontsize=7)

    ax1.legend(loc='lower right')
    ax3.legend(loc='lower right')

    ax1.set_ylabel('speed [$m/s$]')
    ax2.set_ylabel('direction [$degree$]')

    ax3.set_ylabel('speed [$m/s$]')
    ax4.set_ylabel('direction [$degree$]')

    ax1.grid(linestyle=':',linewidth=0.1,color='gray')
    ax2.grid(linestyle=':',linewidth=0.1,color='gray')
    ax3.grid(linestyle=':',linewidth=0.1,color='gray')
    ax4.grid(linestyle=':',linewidth=0.1,color='gray')

    x_ticks, x_label = ticker(years,rmse_speed)
    ax2.set_xticks(x_ticks)
    ax2.set_xticklabels(x_label, rotation=20)

    ax4.set_xticks(x_ticks)
    ax4.set_xticklabels(x_label, rotation=20)
    fig1.savefig(os.path.join(outdir_plots, f"{'-'.join(exps)}_bias_currents_{timeAveraging}_ts.png"))
    fig2.savefig(os.path.join(outdir_plots, f"{'-'.join(exps)}_rmse_currents_{timeAveraging}_ts.png"))


def main(exps,years):
    interm_base=getConfigurationByID('conf.yaml','hvFiles_dir')

    conf = getConfigurationByID('conf.yaml', 'currents')
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')), '-'.join(exps))
    os.makedirs(outdir_plots, exist_ok=True)
    timeAveraging=conf.timeseries_timeAveraging

    plotTimeseries(exps,years,interm_base,outdir_plots,timeAveraging)

