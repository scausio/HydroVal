from utils import getConfigurationByID
import windrose
import os
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import numpy as np
sns.set_theme(style="whitegrid")


def plotRose(module, direction, bin_module, bin_dir, title, outname):
    fig = plt.figure(figsize=(2, 2))
    ax = windrose.WindroseAxes.from_ax()
    ax.bar(direction, module, bins=bin_module, nsector=bin_dir, normed=True, opening=1, edgecolor=None)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    # print (ax._info['table'])

    ax.legend(title='Speed')
    ax.set_legend(prop={'size': 'large'}, loc='right')

    plt.title(title)

    plt.savefig(outname)


def computeSpeed(u, v):
    return np.sqrt(u ** 2 + v ** 2)


def computeDirection(u, v):
    deg = np.rad2deg(np.arctan2(v, u))
    deg[deg < 0] += 360
    deg[deg > 360] -= 360

    # deg=180/np.pi *np.arctan2(v,u)
    # deg[deg<0]=180+np.abs(deg[deg<0])
    print(deg)
    return deg

def main(exps,years):
    interm_base=getConfigurationByID('conf.yaml','hvFiles_dir')

    conf = getConfigurationByID('conf.yaml', 'currents')
    bin_speed=np.arange(conf.spectrum.bin_speed[0],conf.spectrum.bin_speed[1],conf.spectrum.bin_speed[2])
    bin_dir=conf.spectrum.bin_dirs

    for exp in exps:
        outdir_plots = os.path.join(conf.outdir.format(plot_dir=getConfigurationByID('conf.yaml', 'plot_dir')),exp)
        os.makedirs(outdir_plots,exist_ok=True)
        buffer=[]
        for year in years:
            buffer.append( xr.open_dataset(os.path.join(interm_base, f"{exp}_{year}_uvMOOR.nc")))

        ds=xr.concat(buffer,dim='TIME')
        print (ds)
        for mooring in ds.station.values:
            print(f'plotting {mooring}')

            u=ds.mod_u.sel(station=mooring).values
            v=ds.mod_v.sel(station=mooring).values
            print (u)
            model_speed=computeSpeed(u,v)
            model_direction=computeDirection(u,v)
            print (model_direction.shape,model_speed.shape)
            if len(years)>1:
                title = f'{exp} {mooring} {years[0]}-{years[-1]} currents'
                outname=os.path.join(outdir_plots, f'{exp}_{mooring}_{years[0]}-{years[-1]}_rose.png')
            else:
                title = f'{exp} {mooring} {years[0]} currents'
                outname=os.path.join(outdir_plots, f'{exp}_{mooring}_{years[0]}_rose.png')
            plotRose(model_speed, model_direction, bin_speed, bin_dir, title, outname)

