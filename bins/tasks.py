from bjobs import Bjobs
from submit import submit_hov, submit_concatPY, submit_curr, submit_PQ, submit_concatClim,submit_salVol,submit_OC,submit_mld,submit_decim
import xarray as xr
import time
import os
from utils import getConfigurationByID
from glob import glob


def sst(exp,years,outdir,bproj,force=False):
    conf=getConfigurationByID('conf.yaml','sst')
    for year in years:
        cmd=submit_PQ('interpolate_model_2D.py', exp, 'T', year, conf.observationFiles.format(year=year), 'sst', outdir,bproj,force=force)
        if cmd:
            print(cmd)
            Bjobs([cmd])

def sla(exp,years,outdir,bproj,chunk=6,force=False):

    conf = getConfigurationByID('conf.yaml', 'sla')
    cmds = []
    n=chunk
    for year in years:
        if n == 0:
            if cmds:
                print(cmds)
                Bjobs(cmds)
                n = chunk
                cmds = []
        else:
            #SAT available from 1988 to 2018
            cmd=submit_PQ('interpolate_model_SLA.py', exp,'T', year,conf.observationFiles.format(year=year),   'sla', outdir,bproj,force=force)
            if cmd:
                cmds.append(cmd)
                n-=1
    if cmds:
        print(cmds)
        Bjobs(cmds)


def profile_argo(exp, years, outdir, bproj,argoEntry, chunk=6, force=False):
    cmds=[]
    conf = getConfigurationByID('conf.yaml', 'profiles')
    n = chunk
    for year in years:
        if n == 0:
            if cmds:
                print(cmds)
                Bjobs(cmds)
                n = chunk
                cmds = []
        else:
            #ARGO available from 2010 to 2018
            cmd=submit_PQ('interpolate_model.py', exp,'T',year,conf.observationFiles.format(year=year),argoEntry, outdir,bproj,force=force)
            if cmd:
                cmds.append(cmd)
                n -= 1
    if cmds:
        print(cmds)
        Bjobs(cmds)

def profiletimeseries_argo(exp,years,outdir,bproj,argoEntry,chunk=6,force=False):
    cmds = []
    conf = getConfigurationByID('conf.yaml', 'timeseriesArgo')
    n = chunk
    for year in years:
        if n == 0:
           if cmds:
               print(cmds)
               Bjobs(cmds)
               n = chunk
               cmds = []
        else:

            cmd=submit_PQ('interpolate_model.py', exp, 'T', year,conf.observationFiles.format(year=year), argoEntry, outdir,bproj,force=force)
            try:
                os.system(cmd)
                print (f'{cmd} submitted')
            except:
                print (f'{cmd} skipped')
                if cmd:
                    cmds.append(cmd)
                    n -= 1
    if cmds:
       print(cmds)
       Bjobs(cmds)

def hovmoller(exp,years,outdir,bproj,chunk=6,force=False):
    cmds=[]
    n = chunk
    for year in years:
        if n == 0:
            if cmds:
                print(cmds)
                Bjobs(cmds)
                n = chunk
                cmds = []
        else:
            # HOVMOLLER preproc
            #        cmd=submit_PQ('interpolate_model_2D.py', exp, 'T', year, conf.observationFiles.format(year=year), 'sst', outdir,bproj,force=force)
            cmd=submit_hov(exp, year, outdir,bproj,force=force)
            if cmd:
                cmds.append(cmd)
                n -= 1
    if cmds:
        print(cmds)
        Bjobs(cmds)

def currentsMoor(exp,years, outdir,bproj,chunk=6,force=False):
    cmds=[]
    n = chunk
    for year in years:
        if n == 0:
            if cmds:
                print(cmds)
                Bjobs(cmds)
                n = chunk
                cmds = []
        else:
            # CURRENTS rose- emodnet available 2015-2019
            cmd=submit_curr( exp, year, outdir,bproj,force=force)
            if cmd:
                cmds.append(cmd)
                n -= 1
    if cmds:
        print (cmds)
        Bjobs(cmds)
    submit_concatPY('concat_UV.py', exp, years, 'uvMOOR', outdir, force=force)

def salinityVolume(msk,exp,years,outdir,bproj,force=False):
    #submit_salVol( exp, years, outdir,bproj,force=force)
    for year in years:
        submit_salVol(msk,exp, year, outdir, bproj, force=force)
        time.sleep(1)

def mld(exp,years,outdir,bproj,force=False):
    profile_argo(exp,years,outdir,bproj,'argo',force)
    for year in years:
        submit_mld(exp, year, outdir, bproj, force = force)

def decimation(exp,grids,years,outdir,bproj,decim_factor,force=False):
    for year in years:
        for grid in grids:
            submit_decim( exp,grid, year, outdir,bproj,decim_factor,force=force)
            time.sleep(5)



class OverturningCirculation():
    def __init__(self):
        pass

    def meridional(self,exp,years,outdir,bproj,chunk=4,force=False):
        cmds=[]
        n = chunk
        for year in years:
            cmds.append(submit_OC( exp, year, 'moc', outdir, bproj))

        Bjobs(cmds)
        submit_concatPY('concat_OC.py', exp, years, 'ymoc', outdir,force=force)


    def zonal(self,exp, years, outdir, bproj,chunk=4,force=False):
        cmds = []
        n = chunk
        for year in years:
            cmds.append(submit_OC(exp, year, 'zoc', outdir, bproj))
        Bjobs(cmds)
        submit_concatPY('concat_OC.py', exp, years, 'yzoc', outdir,force=force)


class Climatologies():
    def __init__(self):
        pass

    def checkClim_complete(self,filelist):

        while True:
            list1 = []

            for file in filelist:
                list1.append(os.path.isfile(file))

            if all(list1):
                # All elements are True. Therefore all the files exist. Run %run commands
                break
            else:
                # At least one element is False. Therefore not all the files exist. Run FTP commands again
                time.sleep(10)  # wait 10 seconds before checking again

    def computeMonthly_YearlyMean(self, exp, years, grids, outdir, bproj,chunk=6, force=False):
        fileBuffer = []
        cmds=[]
        n = chunk
        for year in years:
            for grid in grids:
                if n == 0:
                    if cmds:
                        print(cmds)
                        Bjobs(cmds)
                        n = chunk
                        cmds = []
                else:
                    print(f'computing monthly climatology for {exp} {year} and grid {grid}')
                    cmd=submit_PQ('clim_monthlyMean_pre.py', exp, grid, year,False, 'monthMean', outdir,bproj, force=force)
                    if cmd:
                        cmds.append(cmd)
                        n -= 1
        if cmds:
            print(cmds)
            Bjobs(cmds)
                #fileBuffer.append(outfile)
                #time.sleep(1)
        #self.checkClim_complete(fileBuffer)

    def computeDailyMean(self, exp, years, grids, outdir, bproj,chunk=6, force=False):
        cmds=[]
        n = chunk
        for year in years:
            for grid in grids:
                if n == 0:
                    if cmds:
                        print(cmds)
                        Bjobs(cmds)
                        n = chunk
                        cmds = []
                else:
                    print(f'computing daily climatology for {year} and grid {grid}')
                    cmd = submit_PQ('clim_dailyMean_pre.py', exp, grid, year, False, 'dailyMean', outdir, bproj,
                                    force=force)
                    if cmd:
                        cmds.append(cmd)
                        n -= 1
        if cmds:
            print(cmds)
            Bjobs(cmds)
    def daily(self, exp, years, grids, outdir, bproj, force=False):

        self.computeDailyMean( exp, years, grids, outdir, bproj, force=force)


    def monthly_yearly(self, exp, years, grids, outdir, bproj, force=False):

        self.computeMonthly_YearlyMean( exp, years, grids, outdir, bproj, force=force)

        # for grid in grids:
        #     print(f'concatenating monthly climatology for grid {grid}')
        #     submit_concatClim('concat_Clim.py', exp, grid, years, 'monthMean', outdir, bproj, force=force)

    def total(self,exp, years, grids, outdir, bproj, force=False):
        self.computeMonthly_YearlyMean(exp, years, grids, outdir, bproj, force=force)
        for grid in grids:
            outfile = os.path.join(outdir, f'{exp}_{grid}_{years[0]}-{years[-1]}_mean.nc')
            if not os.path.exists(outfile):
                buffer=[]
                for year in years:
                    infile = os.path.join(outdir, f'{exp}_{grid}_{year}_yearlyMean.nc')

                    if not os.path.exists(infile):
                        xr.open_dataset(os.path.join(outdir, f'{exp}_{grid}_{year}_monthMean.nc')).mean(dim='month').to_netcdf(infile)
                    buffer.append(xr.open_dataset(infile))
                xr.concat(buffer,dim='year').mean(dim='year').to_netcdf(outfile)

class DomainAverage():
    def __init__(self):
        pass

    def checkClim_complete(self,filelist):

        while True:
            list1 = []

            for file in filelist:
                list1.append(os.path.isfile(file))

            if all(list1):
                # All elements are True. Therefore all the files exist. Run %run commands
                break
            else:
                # At least one element is False. Therefore not all the files exist. Run FTP commands again
                time.sleep(10)  # wait 10 seconds before checking again

    def daily(self, exp, years, grids, outdir, bproj,chunk=6, force=False):
        fileBuffer = []
        cmds=[]
        n = chunk
        for year in years:

            for grid in grids:
                if n == 0:
                    if cmds:
                        print(cmds)
                        Bjobs(cmds)
                        n = chunk
                        cmds = []
                else:
                    print(f'computing domain mean  for {year} and grid {grid}')
                    cmd = submit_PQ('domainAverage_pre.py', exp, grid, year,False, 'domainAverage', outdir,bproj, force=force)
                    #fileBuffer.append(outfile)
                    #time.sleep(1)
                    if cmd:
                        cmds.append(cmd)
                        n -= 1
            if cmds:
                print(cmds)
                Bjobs(cmds)

        #self.checkClim_complete(fileBuffer)
        # for grid in grids:
        #     print(f'concatenating domain mean   for grid {grid}')
        #     submit_concatClim('concat_Clim.py', exp, grid, years, 'domainAverage', outdir, bproj, force=force)

class PointExtraction():
    def __init__(self):
        pass

    def daily(self, exp, years, grids, outdir, bproj, force=False):
        fileBuffer = []
        for year in years:
            for grid in grids:
                    print(f'computing domain mean  for {year} and grid {grid}')
                    cmd = submit_PQ('extractPoint_pre.py', exp, grid, year,False, 'domainAverage', outdir,bproj, force=force)
                    #fileBuffer.append(outfile)
                    #time.sleep(1)


        #self.checkClim_complete(fileBuffer)
        for grid in grids:
            print(f'concatenating domain mean   for grid {grid}')
            submit_concatClim('concat_Clim.py', exp, grid, years, 'domainAverage', outdir, bproj, force=force)