import subprocess
import numpy as np
import time

class Bjobs():
    def __init__(self,jobList):

        self.jobList=jobList
        self.jobIds=self.submitJobs(jobList)
        self.waitJobsEnd()


    def waitJobsEnd(self):
        status=self.checkStatus()
        while not self.allDone(status):
            print (' not ready')
            time.sleep(3)
            status=self.checkStatus()

    def allDone(self,stats):
        stats=np.array(stats)
        return np.all(stats=='DONE')
    
    def findIndex(self,splittedList):
        for i,element in enumerate(splittedList):
            if element in ['PEND', 'RUN', 'DONE']:
                #print ('idx:',i)
                return i
        

    def checkStatus(self):
        status=[]
        for jobId in self.jobIds:
            s=subprocess.run('bjobs %s'%(jobId), capture_output=True,shell=True, text=True).stdout
            sts=s.split('\n')[1].split(' ')#[5]
            idx= self.findIndex(sts)
            print (sts[idx])
            status.append(sts[idx])
        return status

    def submitJobs(self, jobLists):
        jobIds=[]
        for job in jobLists:
            jobout=subprocess.run(job, capture_output=True,shell=True, text=True).stdout
            jobId=jobout.split('<')[1].split('>')[0]
            #print (jobId)
            jobIds.append(jobId)
            time.sleep(5)
        return jobIds


