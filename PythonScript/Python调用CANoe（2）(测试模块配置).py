import time, os, msvcrt
from win32com.client import *
from win32com.client.connect import *

def DoEvents():
    pythoncom.PumpWaitingMessages()
    time.sleep(.1)

def DoEventsUntil(cond):
    while not cond():
        DoEvents()

class CanoeSync(object):
    """Wrapper class for CANoe Application object"""
    Started = False
    Stopped = False
    ConfigPath = ""

    def __init__(self):
        app = DispatchEx('CANoe.Application')
        app.Configuration.Modified = False
        ver = app.Version
        print('Loaded CANoe version ',
              ver.major, '.',
              ver.minor, '.',
              ver.Build, '...', sep='')
        self.App = app
        self.Measurement = app.Measurement
        self.Running = lambda: self.Measurement.Running
        self.WaitForStart = lambda: DoEventsUntil(lambda: CanoeSync.Started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: CanoeSync.Stopped)
        WithEvents(self.App.Measurement, CanoeMeasurementEvents)

    def Start(self):
        if not self.Running():
            self.Measurement.Start()
            self.WaitForStart()

    def Stop(self):
        if self.Running():
            self.Measurement.Stop()
            self.WaitForStop()

    def Load(self, cfgPath):
        # current dir must point to the script file
        cfg = os.path.join(os.curdir, cfgPath)
        cfg = os.path.abspath(cfg)
        print('Opening: ', cfg)
        self.ConfigPath = os.path.dirname(cfg)
        self.Configuration = self.App.Configuration
        self.App.Open(cfg)

    def LoadTestSetup(self, testsetup):
        self.TestSetup = self.App.Configuration.TestSetup
        print(self.ConfigPath)
        path = os.path.join(self.ConfigPath, testsetup)
        print("传入的tse路径：", path)
        # 如果目标 tse 已存在，直接读取，否则添加它,如果已经存在，直接add的话会报错
        tse_count = self.TestSetup.TestEnvironments.Count
        print("add前tse数量:",tse_count)
        _existTse = False
        for _index_tse in range(1, tse_count + 1):
            if self.TestSetup.TestEnvironments.Item(_index_tse).FullName == path:
                testenv = self.TestSetup.TestEnvironments.Item(_index_tse)
                _existTse = True
                break
        if _existTse == False:
            testenv = self.TestSetup.TestEnvironments.Add(path)

        print("add后tse数量:", self.TestSetup.TestEnvironments.Count)

        testenv = CastTo(testenv, "ITestEnvironment2")
         # TestModules property to access the test modules
        self.TestModules = []
        self.TraverseTestItem(testenv, lambda tm: self.TestModules.append(CanoeTestModule(tm)))

    def TraverseTestItem(self, parent, testf):
        for test in parent.TestModules:
            testf(test)
        for folder in parent.Folders:
            found = self.TraverseTestItem(folder, testf)

    def RunTestModules(self):
        """ starts all test modules and waits for all of them to finish"""
        # start all test modules
        for tm in self.TestModules:
            tm.Start()
        # wait for test modules to stop
        while not all([not tm.Enabled or tm.IsDone() for tm in self.TestModules]):
            DoEvents()

class CanoeTestModule:
    """Wrapper class for CANoe TestModule object"""
    def __init__(self, tm):
        self.tm = tm
        self.Events = DispatchWithEvents(tm, CanoeTestEvents)
        self.Name = tm.Name
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tm.Enabled
    def Start(self):
        if self.tm.Enabled:
            self.tm.Start()
            self.Events.WaitForStart()

class CanoeTestEvents:
    """Utility class to handle the test events"""
    def __init__(self):
        self.started = False
        self.stopped = False
        self.WaitForStart = lambda: DoEventsUntil(lambda: self.started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: self.stopped)
    def OnStart(self):
        self.started = True
        self.stopped = False
        print("<", self.Name, " started >")
    def OnStop(self, reason):
        self.started = False
        self.stopped = True
        print("<", self.Name, " stopped >")

class CanoeMeasurementEvents(object):
    """Handler for CANoe measurement events"""
    def OnStart(self):
        CanoeSync.Started = True
        CanoeSync.Stopped = False
        print("< measurement started >")

    def OnStop(self):
        CanoeSync.Started = False
        CanoeSync.Stopped = True
        print("< measurement stopped >")

def main():
    Tester = CanoeSync()
    Tester.Load(r'../bmw2.cfg')
    Tester.LoadTestSetup("TestModule/bmwTest_xml_2.tse")
    Tester.Start()
    Tester.RunTestModules()
    Tester.Stop()
if __name__ == "__main__":
    main()
