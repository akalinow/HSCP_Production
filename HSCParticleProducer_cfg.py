import FWCore.ParameterSet.Config as cms


def createHSCPCandidateMakerProcess(isSignal, isBckg, isSkimmedSample, isData, theGlobalTag,
                                    inputFileList, theOutputFileName, era):

   era_config = None
   if era=="UL16":
      from Configuration.Eras.Era_Run2_2016_cff import Run2_2016
      era_config = Run2_2016
   elif era=="UL17":   
      from Configuration.Eras.Era_Run2_2017_cff import Run2_2017
      era_config = Run2_2017
   elif era=="UL18":   
      from Configuration.Eras.Era_Run2_2018_cff import Run2_2018
      era_config = Run2_2018
   else:
      print "Era "+era+" not known!"
      return None

   process = cms.Process("HSCPAnalysis", era_config)

   process.load("FWCore.MessageService.MessageLogger_cfi")
   process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
   process.load('Configuration.StandardSequences.MagneticField_cff')
   process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
   process.load('Configuration.StandardSequences.Services_cff')

   process.options   = cms.untracked.PSet(
   wantSummary = cms.untracked.bool(True),
      SkipEvent = cms.untracked.vstring('ProductNotFound'),
   )
   process.MessageLogger.cerr.FwkReport.reportEvery = 1000

   process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
   process.source = cms.Source("PoolSource",
                               fileNames = inputFileList,
                               inputCommands = cms.untracked.vstring("keep *", "drop *_MEtoEDMConverter_*_*")
   )
   if(isSignal): process.source.duplicateCheckMode = cms.untracked.string("noDuplicateCheck")  #this has to be removed
   #https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideEDMParametersForModules

   from Configuration.AlCa.GlobalTag import GlobalTag
   process.GlobalTag = GlobalTag(process.GlobalTag, theGlobalTag, '')

   process.HSCPTuplePath = cms.Path()

   ########################################################################
   #Run the Skim sequence if necessary
   if(not isSkimmedSample):
      process.nEventsBefSkim  = cms.EDProducer("EventCountProducer")

      process.load('HLTrigger.HLTfilters.hltHighLevel_cfi')
      process.HSCPTrigger = process.hltHighLevel.clone()
      process.HSCPTrigger.TriggerResultsTag = cms.InputTag( "TriggerResults", "", "HLT" )
      process.HSCPTrigger.andOr = cms.bool( True ) #OR
      process.HSCPTrigger.throw = cms.bool( False )
      if(isData):
         process.HSCPTrigger.HLTPaths = [ #check triggers
            "HLT_PFMET170_NoiseCleaned_v*",
            "HLT_Mu45_eta2p1_v*",
            "HLT_Mu50_v*",
         ]
      elif(isBckg):
         #to be updated to Run2 Triggers, in the meanwhile keep all of them to study trigger efficiency
         process.HSCPTrigger.HLTPaths = [
            "HLT_PFMET170_NoiseCleaned_v*", #check triggers  
            "HLT_Mu45_eta2p1_v*",
            "HLT_Mu50_v*",
         ]
      else:
         #do not apply trigger filter on signal
         process.HSCPTrigger.HLTPaths = ["*"]  
      
   process.HSCPTuplePath += process.nEventsBefSkim + process.HSCPTrigger
   ########################################################################
   #Run the HSCP EDM-tuple Sequence on skimmed sample
   process.nEventsBefEDM   = cms.EDProducer("EventCountProducer")
   process.load("SUSYBSMAnalysis.HSCP.HSCParticleProducer_cff")
   process.HSCParticleProducer.filter =  cms.bool(False)
   process.HSCPTuplePath += process.nEventsBefEDM + process.HSCParticleProducerSeq
   ########################################################################  
   #Only for MC samples, save skimmed genParticles
   if(not isData and (isSignal or isBckg)):
      process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
      process.genParticlesSkimmed = cms.EDFilter("GenParticleSelector",
                                                 filter = cms.bool(False),
                                                 src = cms.InputTag("genParticles"),
                                                 cut = cms.string('pt > 5.0'),
                                                 stableOnly = cms.bool(True)
      )
      process.HSCPTuplePath += process.genParticlesSkimmed
   ########################################################################
   #make the pool output
   process.Out = cms.OutputModule("PoolOutputModule",
                                  outputCommands = cms.untracked.vstring(
                                  "drop *",
                                  "keep EventAux_*_*_*",
                                  "keep LumiSummary_*_*_*",
                                  "keep edmMergeableCounter_*_*_*",
                                  "keep GenRunInfoProduct_*_*_*",
                                  "keep GenEventInfoProduct_generator_*_*",
                                  "keep *_genParticlesSkimmed_*_*",
                                  "keep *_genParticlePlusGeant_*_*",
                                  "keep *_offlinePrimaryVertices_*_*",
                                  "keep recoTracks_generalTracks_*_*",
                                  "keep recoTracks_standAloneMuons_*_*",
                                  "keep recoTrackExtras_standAloneMuons_*_*",
                                  "keep TrackingRecHitsOwned_standAloneMuons_*_*",
                                  "keep recoTracks_globalMuons_*_*",  
                                  "keep recoTrackExtras_globalMuons_*_*",
                                  "keep recoMuons_muons_*_*",
                                  "keep recoMuonTimeExtraedmValueMap_muons_*_*",
                                  "keep edmTriggerResults_TriggerResults_*_*",
                                  "keep *_ak4PFJetsCHS__*", 
                                  "keep recoPFMETs_pfMet__*",     
                                  "keep *_HSCParticleProducer_*_*",
                                  "keep *_HSCPIsolation*_*_*",
                                  "keep *_dedxHitInfo*_*_*",
                                  "keep triggerTriggerEvent_hltTriggerSummaryAOD_*_*",
                                  "keep *_offlineBeamSpot_*_*",
                                  "keep *_MuonSegmentProducer_*_*",
                                  "keep *_g4SimHits_StoppedParticles*_*",
                                  "keep PileupSummaryInfos_addPileupInfo_*_*",
                                  "keep *_dt4DSegments__*",  
                                  "keep *_cscSegments__*",   
                               ),
                               fileName = cms.untracked.string(theOutputFileName),
                               SelectEvents = cms.untracked.PSet(
                                  SelectEvents = cms.vstring('*')
                               ),
   )

   LUMITOPROCESS = []
   if(isData and len(LUMITOPROCESS)>0):
      import FWCore.PythonUtilities.LumiList as LumiList
      process.source.lumisToProcess = LumiList.LumiList(filename = LUMITOPROCESS).getVLuminosityBlockRange()

   if(isBckg or isData):
      process.Out.SelectEvents.SelectEvents =  cms.vstring('HSCPTuplePath')  #take just the skimmed ones
      process.Out.outputCommands.extend(["drop triggerTriggerEvent_hltTriggerSummaryAOD_*_*"])
   else:
      process.Out.SelectEvents = cms.untracked.PSet()
   ########################################################################
   #schedule the sequence
   process.endPath1 = cms.EndPath(process.Out)
   process.schedule = cms.Schedule(process.HSCPTuplePath, process.endPath1)

   return process

