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
    if dataset.split("/")[2].find("Run201")!=-1:
        shortName += "_"+dataset.split("/")[2]
    requestName = shortName+"_EDM_HSCP_Candidates_"+outputDatasetTag
    theGlobalTag = eras_conditions[era]
    outputFileName = 'EDMCandidates.root'
    inputFileList = cms.untracked.vstring()
    
    if runLocal:
        for aFile in localFiles:
            inputFileList.append(aFile)

    prepareCMSSWCfg(isSignal, isBckg, isSkimmedSample,
                    isData, theGlobalTag,
                    inputFileList, outputFileName,
                    era)
                                                              
    ##Modify CRAB3 configuration
    config.JobType.allowUndistributedCMSSW = True
    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = 'tmpConfig.py'
    config.JobType.disableAutomaticOutputCollection = True
    config.JobType.scriptExe = 'runMuonTimingStudy.py'
    config.JobType.inputFiles = ['CMS_GeomTree.root', 'MuonTimingStudy.C', 'Analysis_TOFUtility.h']
    config.JobType.outputFiles = ['EDMCandidates.root','DT_SynchHistos.root']
    
    config.General.requestName = requestName
    config.General.workArea = "Tasks_"+era

    config.Data.inputDBS = 'global'
    config.Data.inputDataset = dataset
    config.Data.outLFNDirBase = outLFNDirBase+outputDatasetTag
    config.Data.publication = True
    config.Data.outputDatasetTag = outputDatasetTag
    
    config.Site.storageSite = storage_element
    
    config.Data.unitsPerJob = eventsPerJob
    config.Data.splitting = 'EventAwareLumiBased'
    config.Data.totalUnits = -1
    config.Data.lumiMask=""
    if dataset.split("/")[2].find("AARun201")!=-1:
        jsonFile = eras_jsons[era]
        command = "wget "+jsonFile
        os.system(command)
        config.Data.lumiMask=jsonFile.split("/")[-1]

    if runLocal:
        os.system("cp tmpConfig.py PSet.py; ./"+config.JobType.scriptExe)
    else:
        out = open('crabTmp.py','w')
        out.write(config.pythonise_())
        out.close()
        os.system("crab submit -c crabTmp.py")
    os.system("rm -f tmpConfig.py crabTmp.py")
#########################################
#########################################
eras_conditions = {
    "UL18":"106X_upgrade2018_realistic_v15_L1v1",
    "UL17":"106X_mc2017_realistic_v8",
    "UL16":"106X_mcRun2_asymptotic_v13",
    }

#Official service: https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/
eras_jsons = {
"UL16":"http://akalinow.web.cern.ch/akalinow/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
"UL17":"http://akalinow.web.cern.ch/akalinow/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt",
"UL18":"http://akalinow.web.cern.ch/akalinow/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
}
########################################################

CMSSW_BASE = os.environ.get("CMSSW_BASE")

##Those are the steering parameters
eventsPerJob = 400000
outLFNDirBase = "/store/user/akalinow/HSCP/"
storage_element="T2_PL_Swierk"
outputDatasetTag = "test14"

isSignal = True
isBckg = False
isData = True
isSkimmedSample = False

#List od DBS datasetsa to be analyzed
datasets = {"/SingleMuon/Run2018A-12Nov2019_UL2018_rsb-v1/AOD",
            #"/SingleMuon/Run2018B-12Nov2019_UL2018-v2/AOD",
            #"/SingleMuon/Run2018C-12Nov2019_UL2018-v2/AOD",
            #"/SingleMuon/Run2018D-12Nov2019_UL2018-v4/AOD"
}

runLocal = False
##List of locally accesible files to be analysed by running the cmsRun on local machine.
localFiles = {'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_1.root',
              #'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_2.root',
              #'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_3.root',
              #'file:///home/akalinow/scratch/CMS/HSCP/Data/HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL18_test7-db2b9d02631f39d56f7dea0071264358/USER/RECO_4.root',
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

