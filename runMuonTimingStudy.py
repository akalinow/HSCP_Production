#!/usr/bin/env python
import os.path
import ROOT
from DataFormats.FWLite import Events, Handle

#First step cfg is provided by Crab
command = "cmsRun -j FrameworkJobReport.xml -p PSet.py"
os.system(command)

makeshared = ROOT.TString(ROOT.gSystem.GetMakeSharedLib())
makeshared.ReplaceAll("-W ", "-Wno-deprecated-declarations -Wno-deprecated -Wno-unused-local-typedefs -Wno-attributes ")
makeshared.ReplaceAll("-Woverloaded-virtual ", " ")
makeshared.ReplaceAll("-Wshadow ", " -std=c++0x -D__USE_XOPEN2K8 ")
print("Compilling with the following arguments:",makeshared)
ROOT.gSystem.SetMakeSharedLib(makeshared.Data())
ROOT.gSystem.SetIncludePath("-I$ROOFITSYS/include")
ROOT.gSystem.Load("libFWCoreFWLite")
ROOT.gSystem.Load("libDataFormatsFWLite.so")
ROOT.gSystem.Load("libAnalysisDataFormatsSUSYBSMObjects.so")
ROOT.gSystem.Load("libDataFormatsVertexReco.so")
ROOT.gSystem.Load("libDataFormatsHepMCCandidate.so")
ROOT.gSystem.Load("libPhysicsToolsUtilities.so")
ROOT.gSystem.Load("libdcap.so")
ROOT.gInterpreter.SetClassAutoparsing(False)
ROOT.FWLiteEnabler.enable()
ROOT.gSystem.CompileMacro('MuonTimingStudy.C')

from ROOT import MuonTimingStudy
MuonTimingStudy("./", "EDMCandidates.root", "DT_SynchHistos.root","ChamberData")
