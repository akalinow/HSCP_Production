#!/usr/bin/env python

import os, re
import commands
import math
import urllib
import glob

import CRABClient
from CRABAPI.RawCommand import crabCommand
from crab3 import *

def createGenSimRecoFramgent(era, withPileUp, generator_fragment):
    
    #premix_switches = "--step GEN,SIM,DIGI,L1,HLT:GRun,RAW2DIGI,L1Reco,RECO, RECOSIM"
    premix_switches = "--step GEN,SIM,DIGI,L1,DIGI2RAW,L1Reco,HLT:GRun,RECO "
    premix_switches = "--step GEN,SIM,DIGI,L1,DIGI2RAW,L1Reco "
    if withPileUp:
         premix_switches = premix_switches.replace("DIGI","DIGI,DATAMIX")
         premix_switches += pileup_inputs[era]+" "
         premix_switches += "--procModifiers premix_stage2 --datamix PreMix "

    if era=="Run2029":
        premix_switches = premix_switches.replace("L1,DIGI2RAW","L1TrackTrigger,L1,DIGI2RAW")
        premix_switches += "--customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000 "
        premix_switches += "--customise Configuration/DataProcessing/Utils.addMonitoring "
        premix_switches += "--customise UserCode/OmtfAnalysis/privateCustomizations.customize_L1TkMuonsGmt "
        premix_switches += "--customise UserCode/OmtfAnalysis/privateCustomizations.customize_outputCommands "     
        
    command = "cmsDriver.py " +\
    "Configuration/GenProduction/python/ThirteenTeV/HSCP/"+generator_fragment+" "+\
    "--processName fullsim " +\
    "--fileout file:FEVTSIM.root " +\
    "--mc --eventcontent FEVTSIM "+\
    premix_switches +\
    eras_conditions[era] +" "+\
    "--customise SimG4Core/CustomPhysics/Exotica_HSCP_SIM_cfi.customise "+\
    "--nThreads 1 "+\
    "--python_filename GEN_SIM_DIGI_RAW_RECO_step_cfg.py -n 2 --no_exec"
    print command
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
                   withPileUp,
                   runLocal):
    
    outputDatasetTag = era+"_"+outputDatasetTag
    requestName = generator_fragment.split("cff")[0]
    requestName = requestName.rstrip("_")
    requestName+="_"+outputDatasetTag
    outputPrimaryDataset = generator_fragment.split("cff")[0].rstrip("_")
    print("requestName:",requestName,          
          "outputPrimaryDataset:",outputPrimaryDataset,
          "outputDatasetTag:",outputDatasetTag)

    ##Modify CRAB3 configuration
    config.JobType.allowUndistributedCMSSW = True
    config.JobType.pluginName = 'PrivateMC'
    config.JobType.psetName = 'GEN_SIM_DIGI_RAW_RECO_step_cfg.py'
    config.JobType.numCores = 1
    config.JobType.maxMemoryMB = 2500
    
    config.General.requestName = requestName
    config.General.workArea = "Tasks_"+era
    
    config.Data.inputDataset = None
    config.Data.outLFNDirBase = outLFNDirBase+outputDatasetTag
    config.Data.publication = True
    config.Data.outputPrimaryDataset = outputPrimaryDataset
    config.Data.outputDatasetTag = outputDatasetTag

    config.Site.storageSite = storage_element
    
    config.Data.unitsPerJob = eventsPerJob
    config.Data.totalUnits = eventsPerJob*numberOfJobs

    fullWorkDirName = config.General.workArea+"/crab_"+config.General.requestName
    requestExists = len(glob.glob(fullWorkDirName))!=0
    if requestExists:
        print("Request with name: {} exists. Skipping.".format(fullWorkDirName))
        return

    createGenSimRecoFramgent(era, withPileUp, generator_fragment)
    
    if runLocal:
        os.system("cp GEN_SIM_DIGI_RAW_RECO_step_cfg.py PSet.py")
    else:
        out = open('crabTmp.py','w')
        out.write(config.pythonise_())
        out.close()
        os.system("crab submit -c crabTmp.py")
        #crabCommand('submit', config = config)
    os.system("rm -f GEN_SIM_DIGI_RAW_step_cfg.py* crabTmp.py*")
#########################################
#########################################
eras_conditions = {
    "Run2029":"--era Phase2C9  --conditions 123X_mcRun4_realistic_v3 --geometry Extended2026D49",
    }

pileup_inputs = {
    "Run2029":" ",
    }

CMSSW_BASE = os.environ.get("CMSSW_BASE")
genFragmentsDirectory = CMSSW_BASE + "/src/"+ "Configuration/GenProduction/python/ThirteenTeV/HSCP/"
generator_fragments = [aFile.split("/")[-1] for aFile in glob.glob(genFragmentsDirectory+"HSCPstop*.py")]

##Those are the steering parameters
generator_fragments = ["HSCPstop_M_800_TuneCP5_13TeV_pythia8_cff.py",
                       #"HSCPstoponlyneutral_M_400_TuneCP5_13TeV_pythia8_cff.py"
]
era = "Run2029"
eventsPerJob = 10
numberOfJobs = 2
outLFNDirBase = "/store/user/akalinow/HSCP/"
storage_element="T2_PL_Swierk"
outputDatasetTag = "test_27_10_2022"
withPileUp = False
runLocal = True
########################################################
for aFragment in generator_fragments:
    prepareCrabCfg(era = era,
                   generator_fragment=aFragment,
                   eventsPerJob=eventsPerJob,
                   numberOfJobs=numberOfJobs,
                   outLFNDirBase = outLFNDirBase, 
                   storage_element=storage_element,
                   outputDatasetTag = outputDatasetTag,
                   withPileUp = withPileUp,
                   runLocal=runLocal)  
########################################################

