#!/usr/bin/env python

import os, re
import commands
import math
import urllib
import glob

import CRABClient
from CRABAPI.RawCommand import crabCommand
from crab3 import *

import FWCore.ParameterSet.Config as cms

#########################################
#########################################
def prepareCMSSWCfg(isSignal, isBckg, isSkimmedSample,
                    isData, theGlobalTag,
                    inputFileList, outputFileName,
                    era):
    
    from HSCParticleProducer_cfg import createHSCPCandidateMakerProcess

    process = createHSCPCandidateMakerProcess(isSignal, isBckg, isSkimmedSample,
                                              isData, theGlobalTag,
                                              inputFileList, outputFileName,
                                              era)
    
    process.SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",
                                            ignoreTotal = cms.untracked.int32(1)
    )
    out = open('tmpConfig.py','w')
    out.write(process.dumpPython())
    out.close()
#########################################
#########################################
def prepareCrabCfg(dataset,
                   eventsPerJob,
                   outLFNDirBase,
                   storage_element,
                   outputDatasetTag,
                   runLocal,
                   localFiles):

    index =  dataset.find("UL")
    if index<0:
        print "Era not coded in the dataset name: ",dataset
        print "Exiting." 
        exit(0)
    era = dataset[index:index+4]
    if era=="UL20":
        era = "UL"+dataset[index+4:index+6]
    outputDatasetTag = era+"_"+outputDatasetTag
    
    shortName = dataset.split("/")[1]
    requestName = shortName+"_EDM_HSCP_Candidates_"+outputDatasetTag
    theGlobalTag = eras_conditions[era]
    outputFileName = 'EDMCandidates.root'
    inputFileList = cms.untracked.vstring()

    print("requestName: ",requestName)
    
    if runLocal:
        for aFile in localFiles:
            inputFileList.append(aFile)

    prepareCMSSWCfg(isSignal, isBckg, isSkimmedSample,
                    isData, theGlobalTag,
                    inputFileList, outputFileName,
                    era)
                                                              
    ##Modify CRAB3 configuration
    config.JobType.allowUndistributedCMSSW = True
    config.JobType.psetName = 'tmpConfig.py'
    
    config.General.requestName = requestName
    config.General.workArea = "Tasks_"+era

    config.Data.inputDBS = 'phys03'
    config.Data.inputDataset = dataset
    config.Data.outLFNDirBase = outLFNDirBase+outputDatasetTag
    config.Data.publication = False
    config.Data.outputDatasetTag = outputDatasetTag

    config.Site.storageSite = storage_element
    
    config.Data.unitsPerJob = eventsPerJob
    config.Data.splitting = 'EventAwareLumiBased'
    config.Data.totalUnits = 400
    config.Data.lumiMask=""
    if dataset.split("/")[2].find("Run201")!=-1:
        command = "wget "+jsonFile
        os.system(command)
        config.Data.lumiMask=jsonFile.split("/")[-1]

    if runLocal:
        os.system("cmsRun tmpConfig.py")
    else:
        crabCommand('submit', config = config)
        #crabCommand('preparelocal', config = config)        
    os.system("rm -f tmpConfig.py")
#########################################
#########################################
eras_conditions = {
    "UL18":"106X_upgrade2018_realistic_v15_L1v1",
    "UL17":"106X_mc2017_realistic_v8",
    "UL16":"106X_mcRun2_asymptotic_v13",
    }

jsonFileRun2016 = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
jsonFileRun2017 = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt",
jsonFileRun2018 = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
########################################################

CMSSW_BASE = os.environ.get("CMSSW_BASE")

##Those are the steering parameters
eventsPerJob = 200
outLFNDirBase = "/store/user/akalinow/HSCP/"
storage_element="T2_PL_Swierk"
outputDatasetTag = "test2"

isSignal = True
isBckg = False
isData = False
isSkimmedSample = False

#List od DBS datasetsa to be analyzed
datasets = {#"/SingleMuon/Run2018A-UL2018_MiniAODv1_NanoAODv2-v1/NANOAOD",
            "/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL16_test5-b6985cf6814c45f9caab5150d241ebd2/USER",
            "/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL17_test5-e7185d9f8cffdc56fdf5e7533dd38538/USER",
            "/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER"
}

runLocal = True
##List of locally accesible files to be analysed by running the cmsRun on local machine.
localFiles = {'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_1.root',
              'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_2.root',
              'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_3.root',
              'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_4.root',
              #'root://eosuser.cern.ch//eos/user/a/akalinow/Data/HSCP/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_1.root',    
}
#datasets = {"/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER"}
########################################################
########################################################

for aDataset in datasets:
    prepareCrabCfg(dataset=aDataset,                   
                   eventsPerJob=eventsPerJob,
                   outLFNDirBase = outLFNDirBase, 
                   storage_element=storage_element,
                   outputDatasetTag = outputDatasetTag,
                   runLocal=runLocal,
                   localFiles=localFiles)
########################################################

