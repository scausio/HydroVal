from bins.tasks import currentsMoor,hovmoller,Climatologies, sst,sla,DomainAverage,profile_argo, profile_argo,salinityVolume,mld,decimation
from run import expsName,years,bproj

class Argo_profiles():
    def __init__(self):
        pass
    def compute(self):
        from run import expsName, years, bproj
        for expName in expsName:
            jid=profile_argo(expName, years, outdir, bproj, 'argo')


    #





    #sst(expName, years, outdir, bproj)
    #sla(expName, years, outdir, bproj)
    #mld(expName, years, outdir,bproj,force=True)
    hovmoller(expName, years, outdir,bproj)
    #currentsMoor(expName, list(range(2015,toYear+1)), outdir, bproj)

    #Climatologies().monthly(expName, years, grids, outdir, bproj)
    # Climatologies().daily(expName, years, grids, outdir, bproj)
    # Climatologies().yearly(expName, years, grids, outdir, bproj) # this produce also monthly clim
    #Climatologies().total(expName, years, grids, outdir, bproj)

    salinityVolume(msk,expName, years, outdir,bproj)

    # #Domain average daily preprocessing is required for TS diagram, timeseries of T, S SSH
    #DomainAverage().daily(expName, years, grids, outdir, bproj)
    #decimation(expName,['T'],years,outdir,bproj,10)

