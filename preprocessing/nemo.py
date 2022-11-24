import xarray as xr
from datetime import datetime
import numpy as np



class Reader:
    def __init__(self,path):
        self.ds=xr.open_dataset(path)
        #result = getattr(Nemo, 'v3')()

    def from_v4(self):
        ds = self.ds
        navlat = ds['nav_lat'].values[ds['nav_lat'].values > 0]
        navlon = ds['nav_lon'].values[ds['nav_lon'].values > 0]
        ds['lat'] = np.unique(navlat.ravel())
        ds['lon'] = np.unique(navlon.ravel())

        ds = ds.rename({'x': 'lon', 'y': 'lat', 'time_counter': 'time'}).set_coords(['lat', 'lon'])
        ds = ds.drop('nav_lat')
        ds = ds.drop('nav_lon')

        try:
            ds = ds.rename({'deptht': 'depth'})
        except:
            try:
                ds = ds.rename({'depthu': 'depth'})
            except:
                try:
                    ds = ds.rename({'depthv': 'depth'})
                except:
                    pass

        try:
            ds = ds.rename({'vo': 'v'})
        except:
            try:
                ds = ds.rename({'uo': 'u'})
            except:
                pass


        ds['lon'].attrs['standard_name'] = 'longitude'
        ds['lat'].attrs['standard_name'] = 'latitude'
        try:
            formatted_time = [datetime.strptime(str(t), '%Y-%m-%d %H:%M:%S') for t in
                              ds.time.values]
        except:
            formatted_time = [datetime.strptime(str(t).split('.')[0], '%Y-%m-%dT%H:%M:%S') for t in
                              ds.time.values]
        ds['time'] = formatted_time
        return ds

    def from_v3(self):
        ds=self.ds
        print(ds)
        ds['lon'] = ds.nav_lon[0]
        ds['lat'] =  ds.nav_lat[:, 0]

        ds = ds.rename({'x': 'lon', 'y': 'lat', 'time_counter': 'time'}).set_coords(['lat', 'lon'])
        ds = ds.drop('nav_lat')
        ds = ds.drop('nav_lon')
        ds = ds.drop('time_counter_bnds')
        try:
            ds = ds.rename({'deptht': 'depth'})
            ds = ds.drop('deptht_bnds')
        except:
            try:
                ds = ds.rename({'depthu': 'depth'})
                ds = ds.drop('depthu_bnds')
            except:
                try:
                    ds = ds.rename({'depthv': 'depth'})
                    ds = ds.drop('depthv_bnds')
                except:
                    pass
        try:
            ds = ds.rename({'vomecrty': 'v'})
        except:
            try:
                ds = ds.rename({'vozocrtx': 'u'})
            except:
                pass
        ds['lon'].attrs['standard_name'] = 'longitude'
        ds['lat'].attrs['standard_name'] = 'latitude'
        try:
            formatted_time = [datetime.strptime(str(t), '%Y-%m-%d %H:%M:%S') for t in
                              ds.time.values]
        except:
            formatted_time = [datetime.strptime(str(t).split('.')[0], '%Y-%m-%dT%H:%M:%S') for t in
                              ds.time.values]
        ds['time'] = formatted_time
        return ds

    def from_medv3(self):
        ds=self.ds

        i=0
        for  element in  ds.nav_lon:
            if 0 in element:
                i+=1
            else:
                print(i)
                ds['lon'] = ds.nav_lon[i]
        ds['lat'] =  ds.nav_lat[:, 0]

        ds = ds.rename({'x': 'lon', 'y': 'lat', 'time_counter': 'time'}).set_coords(['lat', 'lon'])
        ds = ds.drop('nav_lat')
        ds = ds.drop('nav_lon')
        ds = ds.drop('time_instant_bounds')
        ds = ds.drop('time_counter_bounds')
        try:
            ds = ds.rename({'deptht': 'depth'})
            ds = ds.drop('deptht_bnds')
        except:
            try:
                ds = ds.rename({'depthu': 'depth'})
                ds = ds.drop('depthu_bnds')
            except:
                try:
                    ds = ds.rename({'depthv': 'depth'})
                    ds = ds.drop('depthv_bnds')
                except:
                    pass
        try:
            ds = ds.rename({'vomecrty': 'v'})
        except:
            try:
                ds = ds.rename({'vozocrtx': 'u'})
            except:
                pass
        ds['lon'].attrs['standard_name'] = 'longitude'
        ds['lat'].attrs['standard_name'] = 'latitude'
        try:
            formatted_time = [datetime.strptime(str(t), '%Y-%m-%d %H:%M:%S') for t in
                              ds.time.values]
        except:
            formatted_time = [datetime.strptime(str(t).split('.')[0], '%Y-%m-%dT%H:%M:%S') for t in
                              ds.time.values]
        ds['time'] = formatted_time
        return ds

    def from_pqTool(self):
        ds=self.ds
        ds = ds.rename({'longitude': 'lon', 'latitude': 'lat'}).set_coords(['lat', 'lon'])
        ds['lon'].attrs['standard_name'] = 'longitude'
        ds['lat'].attrs['standard_name'] = 'latitude'
        try:
            formatted_time = [datetime.strptime(str(t), '%Y-%m-%d %H:%M:%S') for t in
                              ds.time.values]
        except:
            try:
                formatted_time = [datetime.strptime(str(t).split('.')[0], '%Y-%m-%dT%H:%M:%S') for t in
                                  ds.time.values]
            except:
                formatted_time='mean'

        ds['time'] = formatted_time
        return ds


def u2t(data, xdim='lon'):
    return (data + data.shift({xdim: 1}))/2


def v2t(data, ydim='lat'):
    return (data + data.shift({ydim: 1}))/2