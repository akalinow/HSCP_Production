#!/usr/bin/env python

import os, re
import commands
import math
import urllib
import glob

import CRABClient
from CRABAPI.RawCommand import crabCommand
from crab3 import *

def createGenSimFramgent(era, withPileUp, generator_fragment):
    
    cmssw8_fix = ""
    if era=="16":
        cmssw8_fix = "--outputCommands 'drop *_*_StoppedParticlesName_*' "

    premix_switches = "--step GEN,SIM,DIGI,L1,DIGI2RAW " 
    if withPileUp:
         premix_switches = "--step GEN,SIM,DIGI,DATAMIX,L1,DIGI2RAW "
         premix_switches += pileup_inputs[era]+" "
         premix_switches += "--procModifiers premix_stage2 --datamix PreMix "
        
    command = "cmsDriver.py " +\
    "Configuration/GenProduction/python/ThirteenTeV/HSCP/"+generator_fragment+" "\
    "--fileout file:RECO.root " +\
    "--mc --eventcontent RAWSIM --datatier GEN-SIM-DIGI "+\
    cmssw8_fix +\
    premix_switches +\
    eras_conditions[era] +" "+\
    "--geometry DB:Extended "+\
    "--customise SimG4Core/CustomPhysics/Exotica_HSCP_SIM_cfi.customise "+\
    "--nThreads 4 "+\
    "--runUnscheduled "+\
    "--python_filename GEN_SIM_DIGI_RAW_step_cfg.py -n 2 --no_exec"
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
    config.JobType.pluginName = 'PrivateMC'
    config.JobType.psetName = 'GEN_SIM_DIGI_RAW_step_cfg.py'
    config.JobType.disableAutomaticOutputCollection = True
    config.JobType.scriptExe = 'runAllSteps_UL'+str(era)+'.py'
    config.JobType.outputFiles = ['RECO.root']
    config.JobType.numCores = 4
    config.JobType.maxMemoryMB = 10000
    
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

    fullWorkDirName = config.General.workArea+"/crab_"+config.General.requestName
    requestExists = len(glob.glob(fullWorkDirName))!=0
    if requestExists:
        print("Request with name: {} exists. Skipping.".format(fullWorkDirName))
        return

    createGenSimFramgent(era, withPileUp, generator_fragment)

    if runLocal:
        os.system("cp GEN_SIM_DIGI_RAW_step_cfg.py PSet.py; ./"+config.JobType.scriptExe + "& ")
    else:
        out = open('crabTmp.py','w')
        out.write(config.pythonise_())
        out.close()
        os.system("crab submit -c crabTmp.py")
        #crabCommand('submit', config = config)
    os.system("rm -f GEN_SIM_DIGI_RAW_step_cfg.py* crabTmp.py*")
#########################################
#GT taken from
#https://twiki.cern.ch/twiki/bin/view/CMS/PdmVRun2LegacyAnalysisSummaryTable
#########################################
eras_conditions = {
    "18":"--era Run2_2018 --conditions 106X_upgrade2018_realistic_v15_L1v1 --beamspot Realistic25ns13TeVEarly2018Collision ",
    "17":"--era Run2_2017 --conditions 106X_mc2017_realistic_v8 --beamspot Realistic25ns13TeVEarly2017Collision ",
    "16":"--era Run2_2016 --conditions 106X_mcRun2_asymptotic_v15 --beamspot Realistic25ns13TeV2016Collision "
    }

pileup_inputs = {
    "18":"--pileup_input \"dbs:/Neutrino_E-10_gun/RunIISummer19ULPrePremix-UL18_106X_upgrade2018_realistic_v11_L1v1-v2/PREMIX\" ",
    "17":"--pileup_input \"dbs:/Neutrino_E-10_gun/RunIISummer19ULPrePremix-UL17_106X_mc2017_realistic_v6-v1/PREMIX\" ",
    "16":"--pileup_input \"dbs:/Neutrino_E-10_gun/RunIISummer19ULPrePremix-UL16_106X_mcRun2_asymptotic_v10-v2/PREMIX\" "
    }

CMSSW_BASE = os.environ.get("CMSSW_BASE")
genFragmentsDirectory = CMSSW_BASE + "/src/"+ "Configuration/GenProduction/python/ThirteenTeV/HSCP/"
generator_fragments = [aFile.split("/")[-1] for aFile in glob.glob(genFragmentsDirectory+"HSCPstop*.py")]

##Those are the steering parameters
generator_fragments = ["HSCPstop_M_800_TuneCP5_13TeV_pythia8_cff.py",
                       "HSCPstoponlyneutral_M_400_TuneCP5_13TeV_pythia8_cff.py"]
era = "17"
eventsPerJob = 200
numberOfJobs = 2
outLFNDirBase = "/store/user/akalinow/HSCP/"
storage_element="T2_PL_Swierk"
outputDatasetTag = "test9"
withPileUp = False
runLocal = False
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

