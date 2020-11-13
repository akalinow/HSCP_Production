## Introduction

This is a script for submitting the Ultra Legacy (UL) production to WLCG Grid.
The full simulation chain: GEN-SIM-RECO is made within a single Crab job.
The GEN configuration is created within the [submitJobs.py](submitJobs.py) file, rest
inside [runAllSteps_UL18.py](runAllSteps_UL18.py) files executed on grid.
Configuration files for each step are generated using the cmsDriver with
parameters taken from official [MuonPOGMcMRequests](https://twiki.cern.ch/twiki/bin/view/CMS/MuonPOGMcMRequests).
For example the UL18 configuration was taken from production configuration under this
[link](https://cms-pdmv.cern.ch/mcm/chained_requests?prepid=MUO-chain_RunIISummer19UL18wmLHEGEN_flowRunIISummer19UL18SIM_flowRunIISummer19UL18DIGIPremix_flowRunIISummer19UL18HLT_flowRunIISummer19UL18RECO_flowRunIISummer19UL18MiniAOD_flowRunIISummer19UL18NanoAOD-00011)

The output of the final step: RECO is saved to selected T2 storage elementt (SE), and a dataset is published to
DBS for further usage, like [those test samples](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fphys03&input=dataset%3D%2F*%2Fakalinow-UL*%2FUSER)

## Installation instructions:

* setup the CMSSW_10_6_12 work are according to the
  [TWiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/HSCPRun2Simulation#Instructions_to_produce_UL_HSCP)

* fetch this respository:

``` 
git clone https://github.com/akalinow/HSCP_Production
cd HSCP_Production
```
## Run instructions

The jobs are submitted with a single command:

```
./submitJobs.py
```

The [submitJobs.py](submitJobs.py) script contains following control (parameters)[https://github.com/akalinow/HSCP_Production/blob/main/submitJobs.py#L95-L102]

* **era** - choose the era: "16", "17", "18"
* **eventsPerJob** - number of events to be generated per job. Job for 100 events takes about 40'. Recomended
  job time is 8 hours.
* **numberOfJobs** - number of jobs. Total number generated of events  will be eventsPerJob*numberOfJobs
* **outLFNDirBase** - Logical File Name base directory for storing the output on SE, for example */store/user/akalinow/HSCP/*
  The results will be stored in subdirectories created automatically.
* **storage_element** - name of the SE, for example *T2_PL_Swierk*
* **outputDatasetTag** - tag added to the name of the dataset. The dataset name will contain the name decoded from the genration fragment, for example,
  and the tag, for example: */HSCPstop_M_800_TuneCP5_13TeV_pythia8/akalinow-UL16_test5-b6985cf6814c45f9caab5150d241ebd2/USER*
* **runLocal** - a flag for running a local test. If set to True the Crab job wil not be submitted, indteas a local cmsRun wil be called
  for a single batch of eventsPerJob events