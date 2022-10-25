## Introduction

This is a script for submitting the Phase II production to WLCG Grid.
The full simulation chain: GEN-SIM-RECO is made within a single Crab job.
The full simulation configuration is created within the [submitJobs.py](submitJobs.py) file.

The output of the final step: RECO is saved to selected T2 storage element (SE), and a dataset is published to
DBS for further usage, like [those test samples](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fphys03&input=dataset%3D%2F*%2Fakalinow-UL*%2FUSER)

## Installation instructions:

* setup the CMSSW_12_3_0_pre4 work area according to the
  [TWiki](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideL1TPhase2Instructions#CMSSW_12_3_0_pre4)
  
* add HSCP generator framgents:
```
cd CMSSW_12_3_0_pre4/src
cmsenv
mkdir -p Configuration/GenProduction/
git clone git@github.com:cms-sw/genproductions.git Configuration/GenProduction/
```

## Run instructions

The jobs are submitted with a single command:

```
./submitJobs.py
```

The [submitJobs.py](submitJobs.py) script contains following control [parameters](https://github.com/akalinow/HSCP_Production/blob/PhaseII/submitJobs.py#L117-L124)

* **era** - choose the era: "29"
* **eventsPerJob** - number of events to be generated per job. Job for 100 events takes about 40'. Recommended
  job time is 8 hours, which corresponds to about 1000 events per job.
* **numberOfJobs** - number of jobs. Total number generated of events  will be eventsPerJob*numberOfJobs
* **outLFNDirBase** - Logical File Name base directory for storing the output on SE, for example */store/user/akalinow/HSCP/*
  The results will be stored in subdirectories created automatically.
* **storage_element** - name of the SE, for example *T2_PL_Swierk*
* **outputDatasetTag** - tag added to the name of the dataset. The dataset name will contain the name decoded from the generation fragment, for example,
  and the tag, for example: */HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL16_test5-b6985cf6814c45f9caab5150d241ebd2/USER*
* **runLocal** - a flag for running a local test. If set to *True* the Crab job will not be submitted, instead a local cmsRun will be called
  for a single batch of eventsPerJob events
* **withPileUp** - a flag enabling digitization with pileup
