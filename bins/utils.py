import numpy as np
import xarray as xr
import yaml
import os
import pandas as pd
import shutil
from munch import Munch
import time

umeas={}
umeas['temperature']={}
umeas['temperature']['std']='°C'
umeas['temperature']['mean']='°C'
umeas['temperature']['var']="°Cˆ2"
umeas['temperature']['BIAS']='°C'
umeas['temperature']['RMSE']='°C'
umeas['temperature']['MSE']='°Cˆ2'
umeas['temperature']['cov']='°Cˆ2'
umeas['salinity']={}
umeas['salinity']['std']='PSU'
umeas['salinity']['mean']='PSU'
umeas['salinity']['BIAS']='PSU'
umeas['salinity']['RMSE']='PSU'
umeas['salinity']['var']="PSUˆ2"
umeas['salinity']['MSE']='°Cˆ2'
umeas['salinity']['cov']='°Cˆ2'
umeas['ssh']={}
umeas['ssh']['mean']='m'



stats_longName = {}
stats_longName['std']= 'standard deviation'
stats_longName['var']= 'variance'
stats_longName['mean']= 'mean'
stats_longName['BIAS']= 'BIAS'
stats_longName['MSE']= 'Mean Squared Error'
stats_longName['cov']= 'covariance'


def safeOpenMFdataset(intermFiles):
    ds = xr.open_mfdataset(intermFiles, concat_dim='time')
    _, index = np.unique(ds['time'], return_index=True)
    return ds.isel(time=index)

def getConfigurationByID(conf,confId):
    globalConf = yaml.load(open(conf))
    return Munch.fromDict(globalConf[confId])

def rebuild(conf,keepTemp=False):
    DF = concatenatePickles(os.path.join(conf.paths.outdir, 'tmp_%s'%conf.filenames.experiment))
    DF.to_pickle(
        os.path.join(conf.paths.outdir, conf.filenames.pickleOutname.format(experimentName=conf.filenames.experiment,
                                                                            year=conf.filenames.year,
                                                                           interp=conf.methods.interpolation)))
    if not keepTemp:
        shutil.rmtree(os.path.join(conf.paths.outdir, 'tmp_%s'%conf.filenames.experiment))

def getBlocksIndex(blocksNumb, filesNumb):
    step = int(filesNumb / blocksNumb)
    if step <= 0:
        return [[0, filesNumb + 1]]
    else:
        out = []
        for i in range(filesNumb):
            if i % step == 0:
                out.append(i)
        out.append(filesNumb + 1)
        r = [[i, j] for i, j in zip(out[:-1], out[1:])]
    return r

def concatenatePickles(path):
    return pd.concat([pd.read_pickle(os.path.join(path, f)) for f in os.listdir(path) if not f.startswith('.')],axis=0,ignore_index=True)


def checkOutdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def cut_area(ds,  xmin, xmax, ymin, ymax):
    subset=ds.where((ds['latitude'] >= ymin) &
                   (ds['latitude'] < ymax) &
                   (ds['longitude'] >= xmin) &
                   (ds['longitude'] < xmax)).dropna('obs')
    return subset


def getBins(ds, bins,conf):
    return ds.groupby_bins('depth', bins=bins).apply(lambda x: metrics(x, conf))

def getBins_hs(ds, bins,conf):
    return ds.groupby_bins('depth', bins=bins).apply(lambda x: metrics_hs(x, conf))

def metrics(data,conf,filter=False):
    result = xr.Dataset()
    for name, var in data.variables.items():
        if not name.startswith('model_') and 'model_%s' % name in data.variables:
            diff = data['model_%s' % name] - var
            if filter:
                threshold=threshold_filter(conf, name)
                try:
                    mask=np.abs(diff.isel(model=0).data) < threshold
                except:
                    mask = np.abs(diff.data) < threshold
                diff = diff.isel(obs=mask)
                print ('filtered')
            result['%s_bias' % name] = diff.mean(dim='obs')
            result['%s_rmse' % name] = xr.ufuncs.sqrt((diff ** 2.).mean(dim='obs'))
            result['%s_nobs' % name] = diff.count(dim='obs')
            result['%s' % name] = data['model_%s' % name].mean(dim='obs')
    return result





def metrics_hs(data,conf):
    result = xr.Dataset()
    bias = data['model_temperature'] - data['temperature']

    threshold=threshold_filter(conf, 'temperature')
    mask=np.abs(bias.data) < threshold
    bias = bias.isel(obs=mask)
    result['temperature_rmse' ] = xr.ufuncs.sqrt((bias ** 2.).mean(dim='obs'))
    result['nobs'] = bias.count(dim='obs')
    result['v']=data['v'].mean(dim='obs')
    result['latitude'] =data['latitude'].mean(dim='obs')
    result['longitude'] = data['longitude'].mean(dim='obs')
    return result


def threshold_filter(conf, var):
    return float(conf[var])


def annotateCumulative(ax, strings, colors,xshift=0,yshift=0):
    cc=colors.copy()
    shift = 0
    n=0
    cc.insert(0, 'k')
    print (strings)
    for s, c in zip(strings, cc):
        if n == 0:
            ax.annotate(s.format(v=f"{np.mean(np.array(strings[1:])):.2f}") + " ", xy=(0.2 + xshift + shift, 0.96 + yshift), xycoords='axes fraction', color=c,
                        fontsize=10)
            shift += 0.15
        elif n == len(cc)-1:
            ax.annotate(str(np.round(s,2)) , xy=(0.02 + xshift + shift, 0.96 + yshift), xycoords='axes fraction', color=c,
                        fontsize=10)
            shift += 0.04
        else:
            ax.annotate(str(np.round(s,2)) + ",", xy=(0.02 + xshift + shift, 0.96 + yshift), xycoords='axes fraction', color=c,
                        fontsize=10)
            shift += 0.04
        n+=1


def computeAnomaly(data):
    return np.nanmean(data)-data


def concat_interms(exps, years, interm_tmpl):
    allfiles = []
    for exp in exps:
        print(exp)
        buffer = []
        for year in years:
            print(year)
            buffer.append(xr.open_dataset(interm_tmpl.format(year=year, exp=exp)))
        allfiles.append(xr.concat(buffer, dim='obs'))
    return xr.concat(allfiles, dim='model')

def concat_interms_filled(exps, years, interm_tmpl):
    allfiles = []
    for exp in exps:
        print(exp)
        buffer = []
        for year in years:
            print(year)
            try:
                ds=xr.open_dataset(interm_tmpl.format(year=year, exp=exp))
                print (ds.month)

            except:
                ds=getEmptyMonthlyResult(exp, year)
            buffer.append(ds)
        allfiles.append(xr.concat(buffer, dim='month'))
    return xr.concat(allfiles, dim='model')

def getEmptyMonthlyResult(model_name, year):
    result = xr.Dataset()
    try:
        result['model'] = (('model'), [model_name])
    except:
        result['model'] = (('model'), model_name)
    result['month'] = (('month'), [pd.Timestamp(f"{year}-{month}-01") for month in range(1, 13)])
    result['obs_mld'] = (('model', 'month'), [np.zeros(12) * np.nan])
    result['mod_mld'] = (('model', 'month'), [np.zeros(12) * np.nan])
    result['profiles'] = (('model', 'month'), [np.zeros(12)])
    return result