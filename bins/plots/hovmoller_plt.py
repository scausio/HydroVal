import matplotlib

matplotlib.use('Agg')
import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from cmocean import cm
from utils import getConfigurationByID


def detrend_poly(values):
    x = range(len(values))
    x = np.reshape(x, (len(x), 1))

    valid = np.logical_not(np.isnan(values))
    valid_values = values[valid]

    pf = PolynomialFeatures(degree=2)
    Xp = pf.fit_transform(x)
    model = LinearRegression()
    try:
        model.fit(Xp, valid_values)
        trend = model.predict(Xp)
        detrended = [valid_values[i] - trend[i] + np.nanmean(valid_values) for i in range(0, len(valid_values))]
    except:
        detrended = valid_values
    values[valid] = detrended
    return values


def detrend_simple(values):
    x = range(len(values))
    x = np.reshape(x, (len(x), 1))
    print('len of values', len(x))

    valid = np.logical_not(np.isnan(values))
    print('len of valid', len(valid))
    valid_values = values[valid]
    print('len of valid values', len(valid_values))

    try:
        detrended = [valid_values[i] - valid_values[i - 1] + np.nanmean(valid_values) for i in range(1, len(values))]
        print('len of detrended', len(detrended))
    except:
        detrended = valid_values
    values[valid][:-1] = detrended
    return values


def detrend_series(values):
    x = range(len(values))
    x = np.reshape(x, (len(x), 1))
    print('len of values', len(x))
    model = LinearRegression()

    valid = np.logical_not(np.isnan(values))
    print('len of valid', len(valid))
    valid_values = values[valid]
    print('len of valid values', len(valid_values))

    try:
        model.fit(x, valid_values)
        trend = model.predict(x)

        detrended = [valid_values[i] - trend[i] + np.nanmean(valid_values) for i in range(0, len(values))]
        print('len of detrended', len(detrended))
    except:
        detrended = valid_values
    values[valid] = detrended
    return values

def computeHovAnomaly(data):
    return (np.nanmean(data,axis=1) - data.T).T

def hovmoller(runningDir,base, years, exp, datatype, conf, anomaly=False):
    print('plotting %s' % datatype)
    try:
        buffer=[]
        for year in years:
            ds=xr.open_dataset(os.path.join(base, f"{exp}_{year}_domainHov.nc"))
            buffer.append(ds.isel(time=ds['time.year']==year))
        ds=xr.concat(buffer,dim='time')
        #ds = xr.open_dataset(os.path.join(base, f"{exp}_{years[0]}-{years[-1]}_domainHov.nc"))
    except:
        exit('no input file')

    levels_temp = np.arange(conf.plot_conf.levels_temp[0], conf.plot_conf.levels_temp[1]+conf.plot_conf.levels_temp[2], conf.plot_conf.levels_temp[2])
    levels_sal = np.arange(conf.plot_conf.levels_sal[0], conf.plot_conf.levels_sal[1]+conf.plot_conf.levels_sal[2], conf.plot_conf.levels_sal[2])
    contours_temp = np.arange(conf.plot_conf.contours_temp[0], conf.plot_conf.contours_temp[1],
                              conf.plot_conf.contours_temp[2])
    contours_sal = np.arange(conf.plot_conf.contours_sal[0], conf.plot_conf.contours_sal[1],
                             conf.plot_conf.contours_sal[2])

    if anomaly:
        plot(runningDir,years,  'temperature', ds['depth'], ds, levels_temp, contours_temp, datatype, exp, conf, anomaly=anomaly,
             cmap=cm.balance, )
        plot(runningDir,years, 'salinity', ds['depth'], ds, levels_sal, contours_sal, datatype, exp, conf, anomaly=anomaly,
             cmap=cm.balance, )
    else:
        plot(runningDir,years,  'temperature', ds['depth'], ds, levels_temp, contours_temp, datatype, exp, conf, anomaly=anomaly,
             cmap=cm.thermal, )
        plot(runningDir,years, 'salinity', ds['depth'], ds, levels_sal, contours_sal, datatype, exp, conf, anomaly=anomaly,
             cmap=cm.haline, )
    print('done')



def nearestTens(number):
    return round(number / 10) * 10

def findNearestDepth(depths,target):
    return np.argmin(np.abs(depths - target))

def selectDepths(depths,howMany=9):
    '''

    :param depths: list of depths
    :param howMany: how many depths you need
    :return: index of selected depths
    '''
    return [int(np.floor(i)) for i in np.linspace(0, len(depths) - 1, howMany)]

def getIndexNearestTens(depths):
    print (depths)
    buffer=[]
    for depth in selectDepths(depths):
        buffer.append(int(nearestTens(depths[depth])))
    # print (buffer)
    # # now find nearest tens in your depths
    # idx=[]
    # for d in buffer:
    #     idx.append(findNearestDepth(depths, d))
    # print(depths[idx])
    return buffer


def plot(runningDir,years, variable, depth, dataset, levels, contourLevs, dataType, expName, conf, anomaly, cmap='jet'):
    umeas = {'temperature': 'T [°C]', 'salinity': 'S [PSU]'}
    maxDepth = conf.plot_conf.maxDepth
    detrend = conf.plot_conf.detrend
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'plot_dir')), expName)
    os.makedirs(outdir_plots, exist_ok=True)
    print(dataset[variable].values.shape)

    fig, ax = plt.subplots(figsize=(10, 6))
    xticks = list(years)
    xticks.append(years[-1] + 1)

    #yticks=[int(depth.values[int(np.floor(i))]) for i in np.linspace(0,len(depth)-1,8)]
    depth=depth.values[depth.values<=maxDepth]

    yticks=getIndexNearestTens(depth)
    print (yticks)
    if detrend:
        ds_trended = dataset[variable].values.T
        print('detrending')
        ds = np.array([detrend_poly(lev) for lev in ds_trended])
    else:
        ds = dataset[variable].values.T
    if anomaly:

        ds = dataset[variable].values.T
        ds = computeHovAnomaly(ds)

        im = plt.contourf(range(ds.shape[1]), depth, ds[:len(depth)], levels=levels, extend='both', cmap=cmap)

        cs = plt.contour(np.arange(0.5,ds.shape[1]+0.5,1), range(len(depth)), ds[:len(depth)], contourLevs, colors='k')
        xticks=xticks[:-1]
        plt.xticks([int(i) for i in np.linspace(0, ds.shape[1]-1, len(xticks))], [str(y) for y in xticks],
                   fontsize=8)

    else:
        im = plt.contourf(range(ds.shape[1]), depth, ds[:len(depth)], levels=levels, extend='both', cmap=cmap)
        cs = plt.contour(range(ds.shape[1]), depth, ds[:len(depth)], contourLevs, colors='k')
        plt.xticks([int(i) for i in np.linspace(0, ds.shape[1], len(xticks))], [str(y) for y in xticks],
                   fontsize=8)
    plt.yticks([int(i) for i in np.linspace(0, depth[-1], len(yticks))], [str(y) for y in yticks], fontsize=8)
    cbar = plt.colorbar(im, extend='both')
    cbar.ax.set_title(umeas[variable])

    plt.clabel(cs, cs.levels, inline=True, colors='k', fmt='%.2f', fontsize=7)

    plt.ylabel('Depth (m)', fontsize=14)
    plt.xlabel('Time (years)', fontsize=14)
    plt.setp(ax.get_xticklabels(), rotation=30)

    if detrend:
        if anomaly:
            outname = os.path.join(outdir_plots, f'anomalyHov_{dataType}_{variable}_detrendedPoly_pal.png')
            title = f'Detrended {variable.capitalize()} anomaly {years[0]}-{years[-1]}'
        else:
            outname = os.path.join(outdir_plots, f'hov_{dataType}_{variable}_detrendedPoly_pal.png')
            title = f'Detrended {variable.capitalize()} {years[0]}-{years[-1]}'
    else:
        if anomaly:
            outname = os.path.join(outdir_plots, f'anomalyHov_{dataType}_{variable}.png')

            title = f'{variable.capitalize()} anomaly {years[0]}-{years[-1]}'
        else:
            outname = os.path.join(outdir_plots, f'hov_{dataType}_{variable}.png')
            title = f'{variable.capitalize()} {years[0]}-{years[-1]}'

    plt.ylim([0, maxDepth])

    plt.title(title)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(outname)
    plt.close()


def main(runningDir,exps,years):
    print('*** HOVMOLLER PLOTTING ***')
    interm_base=getConfigurationByID(os.path.join(runningDir,'conf.yaml'),'hvFiles_dir')
    datatypes=['domain']#'point',
    conf = getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'hovmoller')
    for datatype in datatypes:
        print (datatype)
        #hov_difference(exps, datatype)
        for exp in exps:
            hovmoller(runningDir,interm_base, years, exp, datatype, conf)



