import numpy as np
from matplotlib import pyplot as plt
from munch import Munch
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable

def datasetBoundingBox(ds):
    box = Munch()
    box.xmin = min(ds.longitude.values)
    box.ymin = min(ds.latitude.values)
    box.xmax = max(ds.longitude.values)
    box.ymax = max(ds.latitude.values)
    return box


def meridParallelsStepper(diff):
    if diff<2.5:
        return  0.5
    else:
        if diff<5:
            return 1
        else:
            if diff<10:
                return 2
            else:
                if diff < 25:
                    return 5
                else:
                    return 10


def getMeridansNParallels(box):
    start_m=int(box.xmin)
    end_m=int(box.xmax)
    step_m=meridParallelsStepper(end_m-start_m)

    start_p=int(box.ymin)
    end_p=int(box.ymax)
    step_p=meridParallelsStepper(end_p-start_p)

    step=min([step_p,step_m])

    meridians = np.arange(start_m-step,end_m+step, step)
    parallels = np.arange(start_p-step,end_p+step, step)
    return meridians,parallels


def plotMap(ds,cmap, vmin,vmax, outname,resolution='i',title='',cbar_title=''):
    # PLOT MAPS
    fig = plt.figure()
    fig.set_size_inches(8, 6)
    ax = fig.add_subplot(111)

    box=datasetBoundingBox(ds)

    meridians, parallels = getMeridansNParallels(box)
    ax.set_title(title)

    m = Basemap(llcrnrlon=box.xmin, llcrnrlat=box.ymin, urcrnrlat=box.ymax, urcrnrlon=box.xmax, resolution=resolution)
    m.drawcoastlines()
    m.fillcontinents('Whitesmoke')
    m.drawparallels(parallels, labels=[True, False, False, True], linewidth=0.1)
    m.drawmeridians(meridians, labels=[True, False, False, True], linewidth=0.1)

    im = ax.imshow(ds, origin='bottom', cmap=cmap, vmin=vmin,
                         vmax=vmax,
                         extent=[box.xmin,box.xmax, box.ymin, box.ymax])

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.03)

    cbar=plt.colorbar(im, cax=cax)
    cbar.set_label(cbar_title, rotation=270)
    fig.savefig(f'{outname}.png')
    plt.close()