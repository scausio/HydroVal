from bins.submit import submit_job


class ARGO():
    def __init__(self):
        pass
    def profiles(self):
        print('Starting ARGO profile')
        job='ARGO_profile'
        submit_job(job)
        #f'bsub -P {bproj} -q s_long python ./bins/jobs.py {job} '

    def errorEvolution(self):
        print('Starting ARGO profiles error evolution')
        job = 'ARGO_error'
        submit_job(job)

class Hovmoller ():
    def __init__(self):
        pass
    def compute(self):
        print('Starting Hovmoller')
        job = 'HOV'
        submit_job(job)

class SST ():
    def __init__(self,):
        pass
    def compute(self):
        print('Starting SST')
        job = 'SST'
        submit_job(job)

class SLA ():
    def __init__(self):
        pass
    def compute(self):
        print('Starting SLA')
        job = 'SLA'
        submit_job(job)


class TS():
    def __init__(self):
        pass
    def dailyPointProfile(self, x,y):
        print('Starting TS point profile')
        job = 'TS_point'
        submit_job(job,**{'x':x,'y':y})


    def yearlyMean(self):
        print('Starting TS yearly mean')
        job = 'TS_year'
        submit_job(job)

    def monthlyMean(self):
        print('Starting TS monthly mean')
        job = 'TS_month'
        submit_job(job)



class Timeseries():
    def __init__(self):
        pass
    def salinityVol(self):
        print ('Starting salinity volume')
        job = 'ts_SalVol'
        submit_job(job)
    def argo2exps(self):
        print ('Starting timeseries argo 2 exps')
        job = 'ts_argo2Exps'
        submit_job(job)
    def argo(self):
        print ('Starting timeseries argo')
        job = 'ts_argo'
        submit_job(job)
    def domainAverage(self):
        print ('Starting domain average')
        job = 'ts_DomAvg'
        submit_job(job)


    def depthBins(self):
        print ('Starting depth bins')
        job = 'ts_DepBin'
        submit_job(job)


class MVR():
    def __init__(self):
        pass
    def compute(self):
        print('Starting MVR')
        job = 'MVR'
        submit_job(job)


class MLD():
    def __init__(self):
        pass
    def compute(self):
        print('Starting MLD')
        job = 'MLD'
        submit_job(job)


class Decimate():
    def __init__(self):
        pass
    def compute(self,decimFac):
        print('Starting Decimate')
        job = 'decim'
        submit_job(job,**{'decimFac':decimFac})


class Anomaly():
    def __init__(self):
        pass
#expsName,years,bproj,grids
    def hovmoller(self):
        print ('Starting hovmoller anomaly')
        job = 'anom_hov'
        submit_job(job)

    def timeseries(self):
        print ('Starting hovmoller timeseries')
        job = 'anom_ts'
        submit_job(job)

    def maps(self):
        print ('Starting anomaly maps')
        job = 'anom_map'
        submit_job(job)
