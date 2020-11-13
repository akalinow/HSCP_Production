#!/usr/bin/env python

import os

#First step cfg is provided by Crab
command = "cmsRun -j FrameworkJobReport.xml -p PSet.py"
os.system(command)

#HLT step must be made inside different CMSSW version.
command = "scram p CMSSW CMSSW_8_0_33_UL; cd CMSSW_8_0_33_UL;eval `scramv1 runtime -sh`;cd -;\
cmsDriver.py step1 \
--filein file:RECO.root \
--fileout file:HLT.root \
--mc --eventcontent RAWSIM --datatier GEN-SIM-RAW \
--era Run2_2016 \
--conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 \
--step HLT:25ns15e33_v4 \
--outputCommand 'keep *_mix_*_*,keep *_genPUProtons_*_*' \
--inputCommands 'keep *','drop *_*_BMTF_*','drop *PixelFEDChannel*_*_*_*' \
--geometry DB:Extended \
--customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
--nThreads 4 \
--python_filename HLT_step_cfg.py -n -1 --no_exec;\
cmsRun  -j FrameworkJobReport.xml HLT_step_cfg.py"
os.system(command)

#RECO step
command = "cmsDriver.py step1 \
--filein file:HLT.root \
--fileout file:RECO.root \
--mc --eventcontent FEVTDEBUG --datatier GEN-SIM-RAW \
--era Run2_2016 \
--conditions 106X_mcRun2_asymptotic_v13 \
--step RAW2DIGI,L1Reco,RECO,RECOSIM \
--geometry DB:Extended \
--nThreads 4 \
--runUnscheduled \
--python_filename RECO_step_cfg.py -n -1 --no_exec"
os.system(command)
command = "cmsRun  -j FrameworkJobReport.xml RECO_step_cfg.py"
os.system(command)


