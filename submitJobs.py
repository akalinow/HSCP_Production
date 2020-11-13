#!/usr/bin/env python

import os, re
import commands
import math
import urllib
import glob

import CRABClient
from CRABAPI.RawCommand import crabCommand
from crab3 import *

def createGenSimFramgent(era, generator_fragment):
    
    cmssw8_fix = ""
    if era=="16":
        cmssw8_fix = "--outputCommands 'drop *_*_StoppedParticlesName_*' "
        
    command = "cmsDriver.py " +\
    "Configuration/GenProduction/python/ThirteenTeV/HSCP/"+generator_fragment+\
    "--fileout file:RECO.root " +\
    "--mc --eventcontent RAWSIM --datatier GEN-SIM-DIGI "+\
    eras_conditions[era] +" "+\
    cmssw8_fix +\
    "--step GEN,SIM,DIGI,L1,DIGI2RAW "+\
    "--geometry DB:Extended "+\
    "--customise SimG4Core/CustomPhysics/Exotica_HSCP_SIM_cfi.customise "+\
    "--nThreads 4 "+\
    "--runUnscheduled "+\
    "--python_filename GEN_SIM_DIGI_RAW_step_cfg.py -n 2 --no_exec"
    os.system(command)
#########################################
#########################################
def prepareCrabCfg(era,
                   generator_fragment,
                   eventsPerJob,
                   numberOfJobs,
                   outLFNDirBase,
                   storage_element,
                   outputDatasetTag,
                   runLocal):
    
    outputDatasetTag = "UL"+era+"_"+outputDatasetTag
    requestName = generator_fragment.split("cff")[0]
    requestName = requestName.rstrip("_")
    requestName+="_"+outputDatasetTag
    outputPrimaryDataset = generator_fragment.split("cff")[0].rstrip("_")
    print("requestName:",requestName,          
          "outputPrimaryDataset:",outputPrimaryDataset,
          "outputDatasetTag:",outputDatasetTag)

    ##Modify CRAB3 configuration
    config.JobType.allowUndistributedCMSSW = True
    config.JobType.psetName = 'GEN_SIM_DIGI_RAW_step_cfg.py'
    config.JobType.disableAutomaticOutputCollection = True
    config.JobType.scriptExe = 'runAllSteps_UL'+str(era)+'.py'
    config.JobType.outputFiles = ['RECO.root']
    config.JobType.numCores = 4
    config.JobType.maxMemoryMB = 5000
    
    config.General.requestName = requestName
    config.General.workArea = "Tasks_UL"+era
    
    config.Data.inputDataset = None
    config.Data.outLFNDirBase = outLFNDirBase+outputDatasetTag
    config.Data.publication = True
    config.Data.outputPrimaryDataset = outputPrimaryDataset
    config.Data.outputDatasetTag = outputDatasetTag

    config.Site.storageSite = storage_element
    
    config.Data.unitsPerJob = eventsPerJob
    config.Data.totalUnits = eventsPerJob*numberOfJobs

    createGenSimFramgent(era, generator_fragment)
    if runLocal:
        os.system("cp GEN_SIM_DIGI_RAW_step_cfg.py PSet.py; ./"+config.JobType.scriptExe)
    else:    
        crabCommand('submit', config = config)
    os.system("rm -f GEN_SIM_DIGI_RAW_step_cfg.py")
#########################################
#########################################
CMSSW_BASE = os.environ.get("CMSSW_BASE")
genFragmentsDirectory = CMSSW_BASE + "/src/"+ "Configuration/GenProduction/python/ThirteenTeV/HSCP/"
generator_fragments = [aFile.split("/")[-1] for aFile in glob.glob(genFragmentsDirectory+"HSCPstop*.py")]
##TEST
generator_fragments = ["HSCPstop_M_800_TuneCP5_13TeV_pythia8_cff.py"]
                       
eras_conditions = {
    "18":"--era Run2_2018 --conditions 106X_upgrade2018_realistic_v11_L1v1 --beamspot Realistic25ns13TeVEarly2018Collision ",
    "17":"--era Run2_2017 --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision ",
    "16":"--era Run2_2016 --conditions 106X_mcRun2_asymptotic_v13 --beamspot Realistic25ns13TeV2016Collision "
    }

##Those are the steering parameters
era = "18"
eventsPerJob = 100
numberOfJobs = 5
outLFNDirBase = "/store/user/akalinow/HSCP/"
storage_element="T2_PL_Swierk"
outputDatasetTag = "test5"
runLocal = True
########################################################
for aFragment in generator_fragments:
    prepareCrabCfg(era = era,
                   generator_fragment=aFragment,
                   eventsPerJob=eventsPerJob,
                   numberOfJobs=numberOfJobs,
                   outLFNDirBase = outLFNDirBase, 
                   storage_element=torage_element,
                   outputDatasetTag = outputDatasetTag,
                   runLocal=runLocal)  
########################################################
