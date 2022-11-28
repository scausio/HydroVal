from tasks import currentsMoor,hovmoller,Climatologies, sst,sla,DomainAverage,profile_argo, profile_argo,salinityVolume,mld,decimation
import os
from utils import getConfigurationByID
import sys
from plots import profiles_plt,ts_Argo2exps_plt,ts_Argo_plt,hovmoller_plt,sst_plt,sla_plt,TS_plt,ts_SalinityVol_plt,currents_rose_plt,ts_DomainAvg_plt
from plots import ts_DepthBins_plt,profiles_errorEvolution_plt,ts_currents_plt,mvr_plt,anomaly_hovmoller_plt,anomaly_ts_DomainAvg_plt
from plots import anomaly_map_plt,ts_MLD_plt



class Base():

    def __init__(self,runninDir):
        self.runningDir=runninDir
        self.expsName=getConfigurationByID(os.path.join(runninDir,'conf.yaml'), 'expsName')
        fromYear=getConfigurationByID(os.path.join(runninDir,'conf.yaml'), 'fromYear')
        toYear=getConfigurationByID(os.path.join(runninDir,'conf.yaml'), 'toYear')
        self.grids=getConfigurationByID(os.path.join(runninDir,'conf.yaml'), 'grids')
        self.bproj=getConfigurationByID(os.path.join(runninDir,'conf.yaml'), 'bproject')
        self.years=years=list(range(fromYear,toYear+1,1))
        self.outdir = getConfigurationByID(os.path.join(runninDir,'conf.yaml'), 'hvFiles_dir')
        self.msk = getConfigurationByID(os.path.join(runninDir,'conf.yaml'), 'mesh_mask')
        os.makedirs(self.outdir, exist_ok=True)

class Argo(Base):

    def profile(self):
        print (2)
        for expName in self.expsName:
            print (3)
            profile_argo(self.runningDir,expName, self.years, self.outdir, self.bproj, 'argo')
        profiles_plt.main(self.runningDir, self.expsName, self.years, statistics=True, suptitle=True)
    def errorInTime(self):
        for expName in self.expsName:
            profile_argo(self.runningDir,expName, self.years, self.outdir, self.bproj, 'argo')
        profiles_errorEvolution_plt.main(self.runningDir, self.expsName, self.years)
    def timeseries(self):
        for expName in self.expsName:
            profile_argo(self.runningDir,expName, self.years, self.outdir, self.bproj, 'argo')
        ts_Argo_plt.main(self.runningDir, self.expsName, self.years)
    def timeseries2exps(self):
        for expName in self.expsName:
            profile_argo(self.runningDir,expName, self.years, self.outdir, self.bproj, 'argo')
        ts_Argo2exps_plt.main(self.runningDir, self.expsName, self.years)

class SST(Base):

    def compute(self):
        for expName in self.expsName:
            sst(self.runningDir,expName, self.years, self.outdir, self.bproj)
        sst_plt.main(self.runningDir, self.expsName, self.years, statistics=True, suptitle=True)

class SLA(Base):

    def compute(self):
        for expName in self.expsName:
            sla(self.runningDir,expName, self.years, self.outdir, self.bproj)
        sla_plt.main(self.runningDir, self.expsName, self.years, statistics=True, suptitle=True)

class MLD(Base):

    def compute(self):
        for expName in self.expsName:
            mld(self.runningDir,expName, self.years, self.outdir, self.bproj)
        ts_MLD_plt.main(self.runningDir, self.expsName, self.years, statistics=True, suptitle=True)

class MVR(Base):

    def compute(self):
        for expName in self.expsName:
            profile_argo(self.runningDir,expName, self.years, self.outdir, self.bproj, 'argo')
        mvr_plt.main(self.runningDir, self.expsName, self.years,regression=True, statistics=True)

class Hov(Base):

    def compute(self):
        for expName in self.expsName:
            hovmoller(self.runningDir, expName, self.years, self.outdir, self.bproj, force=False)
        hovmoller_plt.main(self.runningDir, self.expsName, self.years)

class TS(Base):

    def monthlyMean(self):
        for expName in self.expsName:
            Climatologies().monthly_yearly(self.runningDir, expName, self.years, self.grids, self.outdir, self.bproj)
        TS_plt.monthlyMean(self.runningDir, self.expsName, self.years)
    def yearlyMean(self):
        for expName in self.expsName:
            Climatologies().monthly_yearly(self.runningDir, expName, self.years, self.grids, self.outdir, self.bproj)
        TS_plt.yearlyMean(self.runningDir, self.expsName, self.years)
    def point(self,x,y):
        for expName in self.expsName:
            Climatologies().daily(self.runningDir, expName, self.years, self.grids, self.outdir, self.bproj)
        TS_plt.dailyPointProfile(self.runningDir, self.expsName, self.years, x, y)

class SalinityVol(Base):

    def compute(self):
        for expName in self.expsName:
            salinityVolume(self.runningDir, self.msk, expName, self.years, self.outdir, self.bproj, )
        ts_SalinityVol_plt.main(self.runningDir, self.expsName, self.years)

class DepthBinning(Base):

    def compute(self):
        for expName in self.expsName:
            DomainAverage().daily(self.runningDir,expName, self.years, self.grids,self.outdir, self.bproj,)
        ts_DepthBins_plt.main(self.runningDir, self.expsName, self.years, statistics=True, suptitle=True)

class DomainAvg(Base):

    def compute(self):
        for expName in self.expsName:
            DomainAverage().daily(self.runningDir,expName, self.years,self.grids, self.outdir, self.bproj)
        ts_DomainAvg_plt.main(self.runningDir, self.expsName, self.years, statistics=True, suptitle=True)

class Anomaly(Base):

    def hov(self):
        for expName in self.expsName:
            Climatologies().monthly_yearly(self.runningDir,expName, self.years,self.grids, self.outdir, self.bproj)
        print ('plotting hov anomaly')
        anomaly_hovmoller_plt.main(self.runningDir, self.expsName, self.years)
    def domainAvg(self):
        for expName in self.expsName:
            Climatologies().monthly_yearly(self.runningDir,expName, self.years,self.grids, self.outdir, self.bproj)
        anomaly_ts_DomainAvg_plt.main(self.runningDir, self.expsName, self.years, statistics=True, suptitle=True)
    def maps(self):
        for expName in self.expsName:
            Climatologies().total(self.runningDir,expName, self.years,self.grids, self.outdir, self.bproj)
            print('plotting map anomaly')
        anomaly_map_plt.main(self.runningDir, self.expsName, self.years)

class Decim(Base):

    def compute(self,decimFact):
        for expName in self.expsName:
            decimation(self.runningDir, expName, self.grids, self.years, self.outdir, self.bproj, decim_factor=decimFact)

# currents_rose_plt.main(expsName,years)
#ts_currents_plt.main(expsName,years))


def main():
    job=sys.argv[1]
    runningDir=sys.argv[2]

    print (f"{job} required")
    if job== 'ARGO_profile':
        Argo(runningDir).profile()
    elif job == 'ARGO_error':
        Argo(runningDir).errorInTime()
    elif job=='ts_argo2Exps':
        Argo(runningDir).timeseries2exps()
    elif job == 'ts_argo':
        Argo(runningDir).timeseries()
    elif job == 'HOV':
        Hov(runningDir).compute()
    elif job == 'SST':
        SST(runningDir).compute()
    elif job == 'SLA':
        SLA(runningDir).compute()
    elif job == 'TS_month':
        TS(runningDir).monthlyMean()
    elif job == 'TS_year':
        TS(runningDir).yearlyMean()
    elif job == 'ts_SalVol':
        SalinityVol(runningDir).compute()
    elif job == 'ts_DomAvg':
        DomainAvg(runningDir).compute()
    elif job == 'ts_DepBin':
        DepthBinning(runningDir).compute()
    elif job == 'MVR':
        MVR(runningDir).compute()
    elif job == 'MLD':
        MLD(runningDir).compute()
    elif job == 'anom_hov':
        Anomaly(runningDir).hov()
    elif job == 'anom_ts':
        Anomaly(runningDir).domainAvg()
    elif job == 'anom_map':
        Anomaly(runningDir).maps()
    elif job.split('_')[0]== 'decim':
        Decim(runningDir).compute(job.split('_')[1])
    elif (job.split('_')[0]=='TS') &(job.split('_')[1]=='point'):
        TS(runningDir).point(job.split('_')[2],job.split('_')[3])
    else:
        print (f'Sorry I am nor able to find {job} as job name.\n'
               f'Available options are: anom_map,anom_ts,anom_hov,MLD,MVR,ts_DepBin,ts_DomAvg\n'
               f'ts_SalVol,TS_year,TS_month,SLA,SST,ts_argo2Exps,ts_argo,ARGO_profile,ARGO_error,TS_point')

if __name__ == '__main__':
    main()