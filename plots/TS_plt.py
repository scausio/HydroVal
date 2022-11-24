import xarray as xr
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (MultipleLocator)
import seaborn as sns
import gsw
from .utils import getConfigurationByID
sns.set_theme(style="whitegrid")

def TS_yearsRange_mean(base,years,exp, conf):

    tmpl='{exp}_T_{year_0}-{year_1}_mean.nc'

    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')), exp)
    os.makedirs(outdir_plots, exist_ok=True)
    ds_all = xr.open_dataset(os.path.join(base, tmpl.format(exp=exp, year_0=years[0], year_1=years[-1])))
    for region in conf.area:
        box = conf.area[region].box
        ds = ds_all.sel(longitude=slice(box.xmin, box.xmax), latitude=slice(box.ymin, box.ymax),
                        depth=slice(box.depth_min, box.depth_max))

        outname=os.path.join(outdir_plots,f'{exp}_{years[0]}-{years[-1]}_{region}_TS_mean.png')

        print (ds)
        ds_sal=ds.salinity.values
        ds_temp=ds.temperature.values

        sal=[]
        temp=[]
        dp=[]
        for i,dpt in enumerate(ds.depth.values):
            print (dpt)
            sal.append(ds_sal[i].flatten())
            temp.append(ds_temp[i].flatten())
            dp.append(np.zeros(len(ds_temp[i].flatten()))+dpt)

        title=''
        plot(temp,sal,dp,outname,conf,region,title)

def TS_yearly_mean(base,years,exp, conf):

    for year in years:
        tmpl = '{exp}_T_{year}_yearlyMean.nc'
        ds_all = xr.open_dataset(os.path.join(base, tmpl.format(exp=exp, year=year)))

        outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')), exp)
        os.makedirs(outdir_plots, exist_ok=True)
        for region in conf.area:
            box=conf.area[region].box
            ds=ds_all.sel(longitude=slice(box.xmin,box.xmax),latitude=slice(box.ymin,box.ymax),depth=slice(box.depth_min,box.depth_max))

            outname=os.path.join(outdir_plots,f'{exp}_{year}_{region}_TS_mean.png')
            print (ds)
            ds_sal=ds.salinity.values
            ds_temp=ds.temperature.values

            sal=[]
            temp=[]
            dp=[]
            for i,dpt in enumerate(ds.depth.values):
                sal.append(ds_sal[i].flatten())
                temp.append(ds_temp[i].flatten())
                dp.append(np.zeros(len(ds_temp[i].flatten()))+dpt)
            title=year
            plot(temp,sal,dp,outname,conf,region,title)


def TS_monthlyMean(base,years,exp, conf):

    tmpl='{exp}_T_{year}_monthMean.nc'
    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')), exp)
    os.makedirs(outdir_plots, exist_ok=True)
    for region in conf.area:
        box = conf.area[region].box
        outname = os.path.join(outdir_plots, f'{exp}_{years[0]}-{years[-1]}_{region}_TS.png')


        buffer=[]
        for year in years:
            ds_all=xr.open_dataset(os.path.join(base, tmpl.format(exp=exp, year=year)))
            ds = ds_all.sel(longitude=slice(box.xmin, box.xmax), latitude=slice(box.ymin, box.ymax),
                            depth=slice(box.depth_min, box.depth_max))
            buffer.append(ds)

        ds=xr.concat(buffer,dim='time')
        ds_sal=ds.salinity.values
        ds_temp=ds.temperature.values

        sal=ds_sal.flatten()
        temp=ds_temp.flatten()
        msk=np.nonzero(sal)
        sal=sal[msk]
        temp=temp[msk]

        # dp=[]
        # for i,dpt in enumerate(ds.depth.values):
        #     print (dpt)
        #     sal.append(ds_sal[i].flatten())
        #     temp.append(ds_temp[i].flatten())
        #     dp.append(np.zeros(len(ds_temp[i].flatten()))+dpt)
        title=f'TS diagram {years[0]}-{years[-1]} {region} monthly mean'
        plot(temp,sal,dp,outname,conf,region,title)


def TS_point(base,years,exp, conf,x,y):

    tmpl='{exp}_T_{year}_dailyMean.nc'

    outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')), exp)
    region='Domain'
    os.makedirs(outdir_plots, exist_ok=True)
    box = conf.area[region].box

    buffer=[]
    for year in years:
        ds_point=xr.open_dataset(os.path.join(base,tmpl.format(exp=exp,year=year))).sel(latitude=y,longitude=x,method='nearest')
        ds_point=ds_point.sel(depth=slice(box.depth_min, box.depth_max))
        print (ds_point)
        ds_sal = ds_point.salinity.values
        ds_temp = ds_point.temperature.values
        msk = np.nonzero(ds_sal)
        dp = []
        for i, dpt in enumerate(ds_point.depth.values):
            print(dpt)
            [dp.append(d) for d in np.zeros(len(ds_temp[:,i].flatten())) + dpt]
        sal = ds_sal.flatten()
        temp = ds_temp.flatten()
        print(len(temp), len(sal))
        title = f'{year}'
        outname = os.path.join(outdir_plots, f'{exp}_{year}_TS_lat{y}_lon{x}.png')
        plot(temp, sal, dp, outname, conf, region, title)

        buffer.append(ds_point)

    outname = os.path.join(outdir_plots, f'{exp}_{years[0]}-{years[-1]}_TS_lat{y}_lon{x}.png')
    ds=xr.concat(buffer,dim='time')

    # ds=xr.open_dataset(f'/work/opa/sc33616/nemo/hydroval_plots/TS/rea16/rea16_TS_{years[0]}-{years[-1]}.nc')
    # sdn_t=xr.open_dataset('/data/opa/bs-mod/data/sdn/SDC_BLS_CLIM_T_1955_2019_0125_m.4Danl.nc').isel(time=range(24,36)).sel(lat=43.5,lon=31,method='nearest')
    # sdn_s = xr.open_dataset('/data/opa/bs-mod/data/sdn/SDC_BLS_CLIM_S_1955_2019_0125_m.4Danl.nc').isel(time=range(24,36)).sel(lat=43.5,lon=31,method='nearest')

    ds_sal=ds.salinity.values
    ds_temp=ds.temperature.values

    # obs_sal=sdn_s.Salinity.values
    # obs_temp=sdn_t.Temperature.values

    msk = np.nonzero(ds_sal)
    sal=[]
    temp=[]
    dp=[]
    for i, dpt in enumerate(ds.depth.values):
        print(dpt)
        [dp.append(d) for d in np.zeros(len(ds_temp[:, i].flatten())) + dpt]
    sal = ds_sal.flatten()
    temp = ds_temp.flatten()
    print (len(temp),len(sal))
    title=f'{years[0]}-{years[-1]}'
    plot(temp, sal,dp, outname, conf, region,title)
    #plot_obs(np.array(ds_temp).flatten(),np.array(ds_sal).flatten(),np.array(obs_temp).flatten(),np.array(obs_sal).flatten(),outname,conf,f'{years[0]}-{years[-1]}')


def plot(temp,sal,dp,outname,conf,region,title=''):
    mint = conf.area[region].plot_axis.ymin #np.nanmin(temp)
    maxt = conf.area[region].plot_axis.ymax#np.nanmax(temp)
    mins = conf.area[region].plot_axis.xmin#np.nanmin(sal)
    maxs = conf.area[region].plot_axis.xmax#np.nanmax(sal)
    tempL = np.linspace(mint , maxt , 200)
    salL = np.linspace(mins , maxs , 200)
    Tg, Sg = np.meshgrid(tempL, salL)
    sigma_theta = gsw.sigma2(Sg, Tg)
    fig, ax = plt.subplots(figsize=(6, 7))

    #c1 = plt.rcParams['axes.prop_cycle'].by_key()['color'][2]

    im=ax.scatter(sal, temp, s=5, lw=0,c=dp,cmap=conf.colorbar.palette,vmin=conf.colorbar.minDepth,vmax=conf.colorbar.maxDepth)
    #ax.plot([0,np.nanmax(temp)],[8.35,8.35],linestyle='dashed', color='r',linewidth=2)
    cb=plt.colorbar(im)
    cb.ax.set_title('Depth[m]')


    #cs = ax.contour(Sg, Tg, sigma_theta,[17.25,19.75,22.05,22.45, 23.85,25.7,26.35,29,33.5 ], colors="k", zorder=50, linestyles='dashed', linewidth=0.5)
    cs = ax.contour(Sg, Tg, sigma_theta,conf.density_contours, colors="gray",linestyle='dotted',
                    zorder=50, linewidth=0.05,alpha=0.8)
    cl = plt.clabel(cs, fontsize=14, inline=True, inline_spacing=-1, fmt="% .2f",colors='k')

    text_kwargs = dict( color='r')

    #[txt.set_bbox(dict(boxstyle='square,pad=0', fc='red')) for txt in cl]
    plt.title(title,fontsize=20)
    #plt.grid(alpha=0.4,linewidth=1,linestyle=':')
    try:
        plt.axis([conf.area[region].plot_axis.xmin,conf.area[region].plot_axis.xmax,
                  conf.area[region].plot_axis.ymin,conf.area[region].plot_axis.ymax])
    except:
        pass
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    #plt.show()
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.ylabel("Temperature ($^\circ$C)",fontsize=18)
    plt.xlabel('Salinity (PSU)',fontsize=18)
    ax.grid(False)
    plt.tight_layout()
    plt.savefig(outname)
    plt.clf()

def plot_obs(temp,sal,obs_temp, obs_sal, outname,conf,region,title=''):
    mint = conf.area[region].plot_axis.ymin #np.nanmin(temp)
    maxt = conf.area[region].plot_axis.ymax#np.nanmax(temp)
    mins = conf.area[region].plot_axis.xmin#np.nanmin(sal)
    maxs = conf.area[region].plot_axis.xmax#np.nanmax(sal)
    tempL = np.linspace(mint , maxt , 200)
    salL = np.linspace(mins , maxs , 200)
    Tg, Sg = np.meshgrid(tempL, salL)
    sigma_theta = gsw.sigma2(Sg, Tg)
    fig, ax = plt.subplots(figsize=(6, 7))


    # im = ax.scatter(sal, temp, s=40, lw=0, label='$Rean$')
    # im = ax.scatter(obs_sal, obs_temp, s=30, marker='o',facecolors='none', edgecolors='k',alpha=0.5, label='$SDN$')

    #c1 = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
    c1=sns.color_palette("husl", 9)[6]

    im = ax.scatter(sal, temp, s=40,marker='o', facecolors='none', edgecolors=c1, alpha=0.3, label='$Rean$')
    im = ax.scatter(obs_sal, obs_temp, s=30, marker='x', c='k', alpha=0.4, label='$SDN$')

    ax.plot([0,np.nanmax(temp)],[8.35,8.35],linestyle='dashed', color='r',linewidth=2)

    cs = ax.contour(Sg, Tg, sigma_theta, [17.25, 19.75, 22.45, 23.85, 25.7, 29, 33.5], colors="gray",linestyle='dotted',
                    zorder=50, linewidth=0.05,alpha=0.8)
    cl = plt.clabel(cs, fontsize=14, inline=True, inline_spacing=-1, fmt="% .2f",colors='k')

    text_kwargs = dict( color='r')
    lg=plt.legend()
    lg.legendHandles[0]._sizes=[30]
    lg.legendHandles[1]._sizes=[60]
    #[txt.set_bbox(dict(boxstyle='square,pad=0', fc='red')) for txt in cl]
    plt.title(title,fontsize=20)
    try:
        plt.axis([conf.area[region].plot_axis.xmin,conf.area[region].plot_axis.xmax,
                  conf.area[region].plot_axis.ymin,conf.area[region].plot_axis.ymax])
    except:
        pass
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.ylabel("Temperature ($^\circ$C)",fontsize=18)
    plt.xlabel('Salinity (PSU)',fontsize=18)
    ax.grid(False)
    plt.tight_layout()
    plt.savefig(outname)


def monthlyMean(exps,years):
    print('*** TS PLOTTING ***')
    base=getConfigurationByID('conf.yaml','hvFiles_dir')
    conf = getConfigurationByID('conf.yaml', 'TS')
    for exp in exps:
        TS_monthlyMean(base, years, exp, conf)

def yearlyMean(exps,years):
    print('*** TS PLOTTING ***')
    base=getConfigurationByID('conf.yaml','hvFiles_dir')
    conf = getConfigurationByID('conf.yaml', 'TS')
    for exp in exps:
        TS_yearly_mean(base, years, exp, conf)

def dailyPointProfile(exps,years, x,y):
    print('*** TS PLOTTING ***')
    # this is for OSR6
    base=getConfigurationByID('conf.yaml','hvFiles_dir')
    conf = getConfigurationByID('conf.yaml', 'TS')
    for exp in exps:
        TS_point(base, years, exp, conf,x,y)

def main(exps,years):
    print('*** TS PLOTTING ***')
    base=getConfigurationByID('conf.yaml','hvFiles_dir')
    conf = getConfigurationByID('conf.yaml', 'TS')
    for exp in exps:
        TS_yearsRange_mean(base, years, exp, conf)