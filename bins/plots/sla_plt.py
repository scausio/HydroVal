import xarray as xr
import numpy as np
import os
import matplotlib.pyplot as plt
from utils import getConfigurationByID,metrics
import seaborn as sns
sns.set_theme(style="whitegrid")

def unbias(data):
    data['sla'] -= data['sla'].mean(dim='obs')
    data['model_sla'] -= data['model_sla'].mean(dim='obs')
    return data

def unbias_along_track(data):
    return data.groupby('track').map(unbias)

def swap_mdt(data):
    if data['model'] in ['bsfs_v3.2', 'bs-nrt_2.2eof3', 'bs-nrt_2.19eof6.1']:
        data['model_sla'] += data['mdt'] - data['old_mdt']
    return data


def main(runningDir,exps, years,statistics, suptitle):
    conf = getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'sla')
    base = getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'hvFiles_dir')
    if len(exps)>1:
        outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'plot_dir')),
                                    '-'.join(exps))
    else:
        outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID(os.path.join(runningDir,'conf.yaml'), 'plot_dir')),exps[0])
    os.makedirs(outdir_plots,exist_ok=True)
    seasons = conf.seasons  # 'DJF', 'MAM', 'JJA', 'SON' or None for all year


    buffer_rmse={}
    buffer_rmse['time']=[]
    buffer_bias={}
    buffer_bias['time']=[]
    for exp in exps:
        buffer_rmse[str(exp)] = []
        buffer_bias[str(exp)]=[]

    for year in years:

        intermediate = xr.open_mfdataset([ os.path.join(base,f'{exp}_T_{year}_sla.nc') for exp in exps],
                                         combine='by_coords', coords='minimal')

        print([i for i in intermediate['model_ssh'].values])
        for index, model in enumerate(intermediate['model']):
            print('%d: %s' % (index, model.data))

        #intermediate = intermediate.sel(model=models)

        if seasons == True:
            print ('seasons')
            intermediate = intermediate.where(intermediate['time'].dt.season == seasons) # FIX IT


        mdt = xr.open_dataset(conf.MDT).get(['mdt', 'old_mdt', 'bathymetry'])

        coords = {coord: intermediate[coord] for coord in ['longitude', 'latitude']}

        mdt = mdt.interp(coords, method='nearest')

        intermediate = xr.merge([intermediate, mdt])
        intermediate = intermediate.where(intermediate['bathymetry'] > 1000.)
        print ([i for i in intermediate['model_ssh'].values])
        intermediate['model_sla'] = intermediate['model_ssh'] - intermediate['mdt']

        # Hack -- these models need the old MDT, add the new and subtract the old
        #old_mdt = intermediate.sel(model=['bsfs_v3.2', 'bs-nrt_2.2eof3', 'bs-nrt_2.19eof6.1'])
        #old_mdt['model_sla'] += old_mdt['mdt'] - old_mdt['old_mdt']
        #intermediate = intermediate.groupby('model').map(swap_mdt)

        intermediate = intermediate.dropna('obs')
        intermediate.coords['date'] = intermediate['time'].astype('datetime64[D]')

        intermediate = intermediate.groupby(intermediate['date']).map(unbias_along_track if conf.along_track else unbias)

        # Use datetime64[M] for monthly or [D] for daily or [W] for weekly
        result = intermediate.groupby(intermediate['time'].astype('datetime64[W]')).apply(lambda x: metrics(x, conf))
        #print ('BIAS',result['sla_bias'])
        result.to_dataframe()
        # plot yearly rmse
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes()
        for model in result['sla_rmse'].transpose('model', 'time'):
            # HERE THE LAST 2 CHARS OF MODEL ARE REMOVED. THIS NEEDS TO REMOVE '_T' FROM FILE NAME
            label =str( model['model'].data)[:-2]
            [buffer_rmse[label].append(i)for i in model.values]
            plt.plot(result['time'], model, '.', linestyle='-', label=label)
        [buffer_rmse['time'].append(i.values) for i in model['time']]
        print(len(buffer_rmse['time']), label, len(buffer_rmse[label]))
        #plt.ylim(0.02, 0.06)
        if suptitle:
            plt.title('Weekly SLA')
        plt.ylabel('RMSE [m]')
        plt.legend(loc='best')#, ncol=(round(len(models) / 4.)))
        plt.grid(True, c='silver', lw=1, ls=':')
        plt.tight_layout()
        fig.autofmt_xdate()
        plt.savefig(os.path.join(outdir_plots,f'sla_rmse_{year}.png'))
        plt.close()

        #plot yearly bias
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes()
        for model in result['sla_bias'].transpose('model', 'time'):
            # HERE THE LAST 2 CHARS OF MODEL ARE REMOVED. THIS NEEDS TO REMOVE '_T' FROM FILE NAME
            label =str( model['model'].data)[:-2]
            print (label)
            print (model.values)
            [buffer_bias[label].append(i) for i in model.values]
            plt.plot(result['time'], model, '.', linestyle='-', label=label)
        [buffer_bias['time'].append(i.values) for i in model['time']]
        print(len(buffer_bias['time']), label, len(buffer_bias[label]))
        #plt.ylim(0.02, 0.06)
        if suptitle:
            plt.title('Weekly SLA')
        plt.ylabel('BIAS [m]')
        plt.legend(loc='best')#, ncol=(round(len(models) / 4.)))
        plt.grid(True, c='silver', lw=1, ls=':')
        plt.tight_layout()
        fig.autofmt_xdate()
        #plt.show()
        #plt.savefig(os.path.join(outdir_plots,f'sla_bias_{year}.png'))
        plt.close()

    fig = plt.figure(figsize=(10, 5))
    ax = plt.axes()
    for k in exps:
        plt.plot(buffer_rmse['time'], buffer_rmse[k], '.', linestyle='-', label=k)

    #plt.ylim(0.02, 0.055)
    if suptitle:
        plt.title('Weekly SLA')
    plt.ylabel('RMSE [m]')
    plt.legend(loc='best')  # , ncol=(round(len(models) / 4.)))
    plt.grid(True, c='silver', lw=1, ls=':')
    plt.tight_layout()
    fig.autofmt_xdate()
    # plt.show()
    plt.savefig(os.path.join(outdir_plots,f'sla_rmse_{years[0]}-{years[-1]}.png') )
    plt.close()

    fig = plt.figure(figsize=(10, 5))
    ax = plt.axes()
    for k in exps:
        plt.plot(buffer_bias['time'], buffer_bias[k], '.', linestyle='-', label=k)

    #plt.ylim(0.02, 0.055)
    if suptitle:
        plt.title('Weekly SLA')
    plt.ylabel('BIAS [m]')
    plt.legend(loc='best')  # , ncol=(round(len(models) / 4.)))
    plt.grid(True, c='silver', lw=1, ls=':')
    plt.tight_layout()
    fig.autofmt_xdate()
    # plt.show()
    #plt.savefig(os.path.join(outdir_plots,f'sla_bias_{years[0]}-{years[-1]}.png') )